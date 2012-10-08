"""
FEZ graphics types
"""

from xnb_parse.binstream import BinaryWriter
from xnb_parse.xnb_reader import VERSION_31
from xnb_parse.xna_types.xna_graphics import Texture2D, FORMAT_COLOR, get_texture_format


class AnimatedTexture(object):
    def __init__(self, width, height, actual_width, actual_height, frames):
        self.width = width
        self.height = height
        self.actual_width = actual_width
        self.actual_height = actual_height
        texture_format = get_texture_format(VERSION_31, FORMAT_COLOR)
        self.frames = []
        for cur_frame in frames:
            texture = Texture2D(texture_format, self.width, self.height, [cur_frame.data])
            new_frame = (cur_frame.duration, texture)
            self.frames.append(new_frame)

    def __str__(self):
        return "AnimatedTexture d:%dx%d a:%dx%d f:%d" % (self.width, self.height, self.actual_width,
                                                         self.actual_height, len(self.frames))

    def export(self, filename):
        for i, cur_frame in enumerate(self.frames):
            cur_frame[1].export("%s\\%04d" % (filename, i))


class Frame(object):
    def __init__(self, duration, data):
        self.duration = duration
        raw_stream = BinaryWriter()
        for col in data:
            raw_stream.write_byte(col.r)
            raw_stream.write_byte(col.g)
            raw_stream.write_byte(col.b)
            raw_stream.write_byte(col.a)
        self.data = raw_stream.serial()

    def __str__(self):
        return "Frame d:%d s:%d" % (self.duration, len(self.data))
