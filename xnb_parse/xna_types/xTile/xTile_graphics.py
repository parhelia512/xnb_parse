"""
xTile graphics types
"""

from __future__ import print_function


class Map(object):
    def __init__(self, id_, description, properties, tilesheets, layers):
        self.id_ = id_
        self.description = description
        self.properties = properties
        self.tilesheets = tilesheets
        self.layers = layers

    def __str__(self):
        return 'Map \'{}\' d:\'{}\' p:{} t:{} l:{}'.format(self.id_, self.description, self.properties,
                                                           self.tilesheets, self.layers)

    def __repr__(self):
        return self.__str__()


class TileSheet(object):
    def __init__(self, id_, description, image_source, sheet_size, tile_size, margin, spacing, properties):
        self.id_ = id_
        self.description = description
        self.image_source = image_source
        self.sheet_size = sheet_size
        self.tile_size = tile_size
        self.margin = margin
        self.spacing = spacing
        self.properties = properties

    def __str__(self):
        return 'TileSheet \'{}\' d:\'{}\' i:\'{}\' s:{} t:{} m:{} s:{} p:{}'.format(self.id_, self.description,
                                                                               self.image_source, self.sheet_size,
                                                                               self.tile_size, self.margin,
                                                                               self.spacing, self.properties)

    def __repr__(self):
        return self.__str__()


class Size(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __str__(self):
        return 'Size w:{} h:{}'.format(self.width, self.height)

    def __repr__(self):
        return self.__str__()


class Layer(object):
    def __init__(self, id_, visible, description, layer_size, tile_size, properties, tiles):
        self.id_ = id_
        self.visible = visible
        self.description = description
        self.layer_size = layer_size
        self.tile_size = tile_size
        self.properties = properties
        self.tiles = tiles

    def __str__(self):
        return 'Layer \'{}\' v:{} d:\'{}\' ls:{} ts:{} p:{} t:{}'.format(self.id_, self.visible, self.description,
                                                                         self.layer_size, self.tile_size,
                                                                         self.properties, self.tiles)

    def __repr__(self):
        return self.__str__()


class Tile(object):
    def __init__(self, tile_index, blend_mode, properties, x, y, tilesheet_id):
        self.tile_index = tile_index
        self.blend_mode = blend_mode
        self.properties = properties
        self.x = x
        self.y = y
        self.tilesheet_id = tilesheet_id

    def __str__(self):
        return 'Tile i:{} b:{} p:{} x:{} y:{} t:{}'.format(self.tile_index, self.blend_mode, self.properties, self.x,
                                                           self.y, self.tilesheet_id)

    def __repr__(self):
        return self.__str__()
