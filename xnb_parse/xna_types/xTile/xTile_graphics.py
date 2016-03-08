"""
xTile objects
"""
import sys

from enum import Enum
from uuid import uuid4

from xnb_parse.file_formats.xml_utils import ET

if sys.version < '3':
    #noinspection PyUnresolvedReferences
    conv = unicode  # pylint: disable-msg=E0602
else:
    conv = str



class BlendMode(Enum):
    Alpha = 0
    Additive = 1


class Size(object):
    width = None
    height = None

    def __init__(self, width, height=None):
        self.width = width
        self.height = height or width

    def __str__(self):
        return '<Size: {}x{}>'.format(self.width, self.height)

    def __repr__(self):
        return self.__str__()

    def xml(self, parent=None, xml_tag='Size'):
        if parent is None:
            root = ET.Element(xml_tag)
        else:
            root = ET.SubElement(parent, xml_tag)

        root.set('width', str(self.width))
        root.set('height', str(self.height))

        return root


class Component(object):
    id_ = None
    properties = None

    def __init__(self, id_=None):
        self.id_ = id_ or uuid4().__str__()
        self.properties = {}

    def __str__(self):
        return '<Component: \'{}\'>'.format(self.id_)

    def __repr__(self):
        return self.__str__()


class DescribedComponent(Component):
    description = None

    def __init__(self, id_, description=None):
        super(DescribedComponent, self).__init__(id_)
        self.description = description or ''

    def __str__(self):
        return '<DescribedComponent: \'{}\', \'{}\'>'.format(self.id_, self.description)


class TileSheet(DescribedComponent):
    map_ = None
    image_source = None
    sheet_size = None
    tile_size = None
    margin = None
    spacing = None

    def __init__(self, id_, map_, image_source, sheet_size, tile_size):
        super(TileSheet, self).__init__(id_, None)
        self.map_ = map_
        self.image_source = image_source
        self.sheet_size = sheet_size
        self.tile_size = tile_size
        self.margin = self.spacing = Size(0, 0)

    def __str__(self):
        return '<TileSheet: \'{}\', \'{}\'>'.format(self.id_, self.description)

    def xml(self, parent=None):
        if parent is None:
            root = ET.Element('TileSheet')
        else:
            root = ET.SubElement(parent, 'TileSheet')

        root.set('Id', self.id_)
        root.set('Map', self.map_.id_)
        if self.description is not None:
            root.set('Description', self.description)
        if self.properties is not None:
            properties = ET.SubElement(root, 'Properties')
            for key, value in self.properties.items():
                property_ = ET.SubElement(properties, 'Property')
                property_.set('key', conv(key))
                property_.text = conv(value)

        if self.image_source is not None:
            root.set('ImageSource', self.image_source)
        if self.sheet_size is not None:
            self.sheet_size.xml(root, 'SheetSize')
        if self.tile_size is not None:
            self.tile_size.xml(root, 'TileSize')
        if self.margin is not None:
            self.margin.xml(root, 'Margin')
        if self.spacing is not None:
            self.spacing.xml(root, 'Spacing')


class Tile(Component):
    layer = None

    def __init__(self, layer):
        super(Tile, self).__init__()
        self.layer = layer

    @property
    def blend_mode(self):
        raise NotImplementedError()

    @property
    def tilesheet(self):
        raise NotImplementedError()

    @property
    def tile_index(self):
        raise NotImplementedError()

    def xml(self, parent=None, x=0, y=0):
        raise NotImplementedError()

    def __str__(self):
        return '<Tile: \'{}\'>'.format(self.id_)


class StaticTile(Tile):
    def __init__(self, layer, tilesheet, blend_mode, tile_index):
        super(StaticTile, self).__init__(layer)
        self._blend_mode = blend_mode
        self._tilesheet = tilesheet
        self._tile_index = tile_index

    @property
    def blend_mode(self):
        return self._blend_mode

    @property
    def tilesheet(self):
        return self._tilesheet

    @property
    def tile_index(self):
        return self._tile_index

    def xml(self, parent=None, x=-1, y=-1):
        if parent is None:
            root = ET.Element('StaticTile')
        else:
            root = ET.SubElement(parent, 'StaticTile')

        root.set('Id', self.id_)
        root.set('Layer', self.layer.id_)

        if self.properties is not None and len(self.properties) > 0:
            properties = ET.SubElement(root, 'Properties')
            for key, value in self.properties.items():
                property_ = ET.SubElement(properties, 'Property')
                property_.set('key', conv(key))
                property_.text = conv(value)

        if x >= 0 and y >= 0:
            location = ET.SubElement(root, 'Location')
            location.set('x', conv(x))
            location.set('y', conv(y))

        blend_mode = ET.SubElement(root, 'BlendMode')
        blend_mode.text = conv(self._blend_mode)

        tilesheet = ET.SubElement(root, 'TileSheet')
        tilesheet.text = self.tilesheet.id_

        tile_index = ET.SubElement(root, 'TileIndex')
        tile_index.text = conv(self._tile_index)

    def __str__(self):
        return '<StaticTile: \'{}\'>'.format(self.id_)


class AnimatedTile(Tile):
    def __init__(self, layer, tile_frames, frame_interval):
        super(AnimatedTile, self).__init__(layer)
        self.tile_frames = tile_frames
        self.frame_interval = frame_interval
        self.animation_interval = frame_interval * len(tile_frames)

    def _get_current_frame(self):
        animation_time = self.layer.map_.elapsed_time % self.animation_interval
        current_index = animation_time // self.frame_interval
        return self.tile_frames[current_index]

    @property
    def blend_mode(self):
        current_frame = self._get_current_frame()
        return current_frame.blend_mode

    @property
    def tilesheet(self):
        current_frame = self._get_current_frame()
        return current_frame.tilesheet

    @property
    def tile_index(self):
        current_frame = self._get_current_frame()
        return current_frame.tile_index

    def xml(self, parent=None, x=0, y=0):
        if parent is None:
            root = ET.Element('AnimatedTile')
        else:
            root = ET.SubElement(parent, 'AnimatedTile')

        root.set('Id', self.id_)
        root.set('Layer', self.layer.id_)

        if self.properties is not None and len(self.properties) > 0:
            properties = ET.SubElement(root, 'Properties')
            for key, value in self.properties.items():
                property_ = ET.SubElement(properties, 'Property')
                property_.set('key', conv(key))
                property_.text = conv(value)

        location = ET.SubElement(root, 'Location')
        location.set('x', conv(x))
        location.set('y', conv(y))

        frame_interval = ET.SubElement(root, 'FrameInterval')
        frame_interval.text = conv(self.frame_interval)

        tile_frames = ET.SubElement(root, 'TileFrames')
        for tile_frame in self.tile_frames:
            tile_frame.xml(tile_frames)

    def __str__(self):
        return '<AnimatedTile: \'{}\'>'.format(self.id_)


class Layer(DescribedComponent):
    map_ = None
    tilesheets = None
    layer_size = None
    tile_size = None
    tiles = None
    visible = False

    def __init__(self, id_, map_, layer_size, tile_size):
        super(Layer, self).__init__(id_)
        self.map_ = map_
        self.tilesheets = map_.tilesheets
        self.layer_size = layer_size
        self.tile_size = tile_size
        self.tiles = [[None for x in range(layer_size.width)] for y in range(layer_size.height)]
        self.visible = True

    def __str__(self):
        return '<Layer: \'{}\', \'{}\'>'.format(self.id_, self.description)

    def xml(self, parent=None):
        if parent is None:
            root = ET.Element('Layer')
        else:
            root = ET.SubElement(parent, 'Layer')

        root.set('Id', self.id_)
        root.set('Map', self.map_.id_)
        root.set('Visible', conv(self.visible))

        if self.description is not None:
            root.set('Description', self.description)
        if self.properties is not None:
            properties = ET.SubElement(root, 'Properties')
            for key, value in self.properties.items():
                property_ = ET.SubElement(properties, 'Property')
                property_.set('key', conv(key))
                property_.text = conv(value)

        tilesheets = ET.SubElement(root, 'TileSheets')
        for tilesheet in self.tilesheets:
            sub_element = ET.SubElement(tilesheets, 'TileSheet')
            sub_element.set('Id', tilesheet.id_)

        if self.layer_size is not None:
            self.layer_size.xml(root, 'LayerSize')
        if self.tile_size is not None:
            self.tile_size.xml(root, 'TileSize')

        tiles = ET.SubElement(root, 'Tiles')
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile is not None:
                    tile.xml(tiles, x, y)


class Map(DescribedComponent):
    tilesheets = None
    layers = None
    elapsed_time = None

    def __init__(self, id_=None):
        super(Map, self).__init__(id_ or 'Untitled map', None)
        self.tilesheets = []
        self.layers = []
        self.elapsed_time = 0

    def get_tilesheet(self, tilesheet_id):
        return [tilesheet for tilesheet in self.tilesheets if tilesheet.id_ == tilesheet_id][0]

    def __str__(self):
        return '<Map: \'{}\', \'{}\'>'.format(self.id_, self.description)

    def xml(self):
        root = ET.Element('Map')

        root.set('Id', self.id_)
        if self.description is not None:
            root.set('Description', self.description)
        if self.properties is not None:
            properties = ET.SubElement(root, 'Properties')
            for key, value in self.properties.items():
                property_ = ET.SubElement(properties, 'Property')
                property_.set('key', conv(key))
                property_.text = conv(value)

        tilesheets = ET.SubElement(root, 'TileSheets')
        for tilesheet in self.tilesheets:
            tilesheet.xml(tilesheets)

        layers = ET.SubElement(root, 'Layers')
        for layer in self.layers:
            layer.xml(layers)
        return root
