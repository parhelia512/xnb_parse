"""
XNB parser
"""

from xnb_parse.binstream import BinaryReader, BinaryWriter
from xnb_parse.xna_native import decompress
from xnb_parse.type_reader_manager import ReaderError


XNB_SIGNATURE = 'XNB'
PLATFORM_WINDOWS = 'w'
PLATFORM_XBOX = 'x'
PLATFORM_MOBILE = 'm'
PROFILE_REACH = 0
PROFILE_HIDEF = 1
VERSION_30 = 3
VERSION_31 = 4
VERSION_40 = 5


class XNBReader(BinaryReader):
    platforms = {PLATFORM_WINDOWS: 'W', PLATFORM_XBOX: 'X', PLATFORM_MOBILE: 'M'}
    versions = {VERSION_30: '30', VERSION_31: '31', VERSION_40: '40'}
    profiles = {PROFILE_REACH: 'r', PROFILE_HIDEF: 'h'}

    _profile_mask = 0x7f
    _compress_mask = 0x80

    _header = '3s c B B I'

    def __init__(self, data, file_platform=PLATFORM_WINDOWS, file_version=VERSION_40, graphics_profile=PROFILE_REACH,
                 compressed=False, type_reader_manager=None, parse=True):
        BinaryReader.__init__(self, data, big_endian=False)
        self.file_platform = file_platform
        self.file_version = file_version
        self.graphics_profile = graphics_profile
        self.compressed = compressed
        self.type_reader_manager = type_reader_manager
        self.type_readers = []
        self.shared_objects = []
        self.content = None
        self.parsed = False
        if parse:
            self.parse()

    def __str__(self):
        return 'XNB %s%s%s s%d' % (self.platforms[self.file_platform], self.versions[self.file_version],
                                   self.profiles[self.graphics_profile], len(self.data))

    def parse(self):
        if self.type_reader_manager is None:
            raise ValueError('No type reader manager')
        if self.parsed:
            return self.content

        print 'Type readers:'
        reader_count = self.read('7b')
        for _ in range(reader_count):
            reader_name = self.read('str')
            reader_version = self.read('s4')
            reader_type = self.type_reader_manager.get_type(reader_name)
            reader = reader_type(self, reader_version)
            self.type_readers.append(reader)
            print reader

        shared_count = self.read('7b')

        print 'Asset:'
        self.content = self.read_object()
        print self.content

        for i in range(shared_count):
            print 'Shared resource %d:' % i
            obj = self.read_object()
            self.shared_objects.append(obj)

        if self.remaining():
            print 'remaining: %d' % self.remaining()
        self.parsed = True
        return self.content

    @classmethod
    def load(cls, data, type_reader_manager=None, parse=True):
        stream = BinaryReader(data, big_endian=False)
        (sig, platform, version, attribs, size) = stream.unpack(cls._header)
        if sig != XNB_SIGNATURE:
            raise ValueError('bad sig: %s' % repr(sig))
        if platform not in cls.platforms:
            raise ValueError('bad platform: %s' % repr(platform))
        if version not in cls.versions:
            raise ValueError('bad version: %s' % repr(version))
        if len(data) != size:
            raise ValueError('bad size: %d != %d' % (len(data), size))
        compressed = False
        profile = 0
        if version >= VERSION_40:
            profile = attribs & cls._profile_mask
            if profile not in cls.profiles:
                raise ValueError('bad profile: %s' % repr(profile))
        if version >= VERSION_30:
            compressed = bool(attribs & cls._compress_mask)
            size -= stream.calc_size(cls._header)
        if compressed:
            uncomp = stream.read('u4')
            size -= stream.size('u4')
            content_comp = stream.pull(size)
            content = decompress(content_comp, uncomp)
        else:
            content = stream.pull(size)
        return cls(content, platform, version, profile, compressed, type_reader_manager, parse)

    def save(self, compress=False):
        stream = BinaryWriter(big_endian=False)
        attribs = 0
        if self.file_platform not in self.platforms:
            raise ValueError('bad platform: %s' % repr(self.file_platform))
        if self.file_version not in self.versions:
            raise ValueError('bad version: %s' % repr(self.file_version))
        if self.file_version >= VERSION_40:
            if self.graphics_profile not in self.profiles:
                raise ValueError('bad profile: %s' % repr(self.graphics_profile))
            attribs |= self.graphics_profile & self._profile_mask
        do_compress = False
        if self.file_version >= VERSION_30:
            if compress:
                do_compress = True
                attribs |= self._compress_mask
        if do_compress:
            raise ValueError('Recompression not supported')
        else:
            data = self.data
            size = len(data) + stream.calc_size(self._header)
        stream.pack(self._header, XNB_SIGNATURE, self.file_platform, self.file_version, attribs, size)
        stream.extend(data)
        return stream.serial()

    def read_object(self):
        type_reader = self.read_type_id()
        if type_reader is None:
            print 'null'
            return None
        print 'Type: %s' % type_reader.target_type
        return type_reader.read()

    def read_type_id(self):
        type_id = self.read('7b')
        if type_id == 0:
            # null object
            return None
        if type_id > len(self.type_readers):
            raise ReaderError("type id out of range: %d > %d" % (type_id, len(self.type_readers)))
        return self.type_readers[type_id - 1]