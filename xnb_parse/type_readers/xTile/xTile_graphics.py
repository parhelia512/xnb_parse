"""
xTile graphics type readers
"""

from __future__ import print_function

from xnb_parse.type_reader import (TypeReaderPlugin, BaseTypeReader)
from xnb_parse.xna_types.xTile.xTile_graphics import *

# avoiding circular import
PLATFORM_WINDOWS = b'w'


class XtileMapReader(BaseTypeReader, TypeReaderPlugin):
    target_type = 'xTile.Map'
    reader_name = 'xTile.Pipeline.TideReader'

    def read(self):
        if self.file_platform == PLATFORM_WINDOWS:
            data_length = self.stream.read_int32()

            magic_word = self.stream.read(6)
            assert magic_word == b'tBIN10', 'Wrong magic word: {}'.format(magic_word)

            map_ = Map()
            map_.id_ = self.stream.read_long_string()
            map_.description = self.stream.read_long_string()
            map_.properties = self.read_properties()
            map_.tilesheets = self.read_tilesheets(map_)
            map_.layers = self.read_layers(map_)

            return map_
        else:
            raise NotImplementedError('Only windows support at this moment')

    def read_properties(self):
        property_count = self.stream.read_int32()

        result = {}
        for i in range(property_count):
            key = self.stream.read_long_string()
            type_ = self.stream.read_7bit_encoded_int()

            if type_ == 0:  # bool
                value = self.stream.read_boolean()
            elif type_ == 1:  # int
                value = self.stream.read_int32()
            elif type_ == 2:  # float
                value = self.stream.read_single()
            elif type_ == 3:  # string
                value = self.stream.read_long_string()
            else:
                raise ValueError('Unexpected type')

            result[key] = value

        return result

    def read_tilesheets(self, map_):
        tilesheet_count = self.stream.read_int32()

        result = []
        for _ in range(tilesheet_count):
            tilesheet = self.read_tilesheet(map_)
            result.append(tilesheet)

        return result

    def read_tilesheet(self, map_):
        id_ = self.stream.read_long_string()
        description = self.stream.read_long_string()
        image_source = self.stream.read_long_string()
        sheet_size = self.read_size()
        tile_size = self.read_size()
        margin = self.read_size()
        spacing = self.read_size()
        properties = self.read_properties()

        tilesheet = TileSheet(id_, map_, image_source, sheet_size, tile_size)
        tilesheet.description = description
        tilesheet.margin = margin
        tilesheet.spacing = spacing
        tilesheet.properties = properties

        return tilesheet

    def read_size(self):
        width = self.stream.read_int32()
        height = self.stream.read_int32()

        return Size(width, height)

    def read_layers(self, map_):
        layers_count = self.stream.read_int32()

        result = []
        for _ in range(layers_count):
            layer = self.read_layer(map_)
            result.append(layer)

        return result

    def read_layer(self, map_):
        id_ = self.stream.read_long_string()
        visible = self.stream.read_boolean()
        description = self.stream.read_long_string()
        layer_size = self.read_size()
        tile_size = self.read_size()

        layer = Layer(id_, map_, layer_size, tile_size)
        layer.description = description
        layer.visible = visible
        layer.properties = self.read_properties()
        layer.tiles = self.read_tiles(layer)

        return layer

    def read_static_tile(self, layer, tilesheet):
        tile_index = self.stream.read_int32()
        blend_mode = BlendMode(self.stream.read_7bit_encoded_int())  # enum(Alpha, Additive)

        static_tile = StaticTile(layer, tilesheet, blend_mode, tile_index)
        static_tile.properties = self.read_properties()

        return static_tile

    def read_animated_tile(self, layer):
        frame_interval = self.stream.read_int32()
        tile_frame_count = self.stream.read_int32()
        tile_frames = self.read_animation_tiles(layer, tile_frame_count)

        animated_tile = AnimatedTile(layer, tile_frames, frame_interval)
        animated_tile.properties = self.read_properties()

        return animated_tile

    def read_tiles(self, layer):
        layer_size = layer.layer_size
        result = [[None for x in range(layer_size.width)] for y in range(layer_size.height)]
        tilesheet = None

        for y in range(layer_size.height):
            x = 0
            while x < layer_size.width:
                ch = self.stream.read_char()
                if ch == 'T':  # tilesheet id
                    tilesheet_id = self.stream.read_long_string()
                    tilesheet = layer.map_.get_tilesheet(tilesheet_id)

                elif ch == 'N':  # nulls
                    null_count = self.stream.read_int32()
                    x += null_count

                elif ch == 'S':  # static tile
                    if tilesheet is None:
                        raise ValueError('tilesheet')

                    result[y][x] = self.read_static_tile(layer, tilesheet)
                    x += 1

                elif ch == 'A':  # animated tile
                    if tilesheet is None:
                        raise ValueError('tilesheet')

                    result[y][x] = self.read_animated_tile(layer)
                    x += 1
                else:
                    raise ValueError('ch: {}'.format(ch))

        return result

    def read_animation_tiles(self, layer, tile_frame_count):
        tilesheet = None
        result = []
        while tile_frame_count > 0:
            ch = self.stream.read_char()
            if ch == 'T':  # tilesheet id
                tilesheet_id = self.stream.read_long_string()
                tilesheet = layer.map_.get_tilesheet(tilesheet_id)

            elif ch == 'S':  # static tile
                if tilesheet is None:
                    raise ValueError('tilesheet')

                tile_frame = self.read_static_tile(layer, tilesheet)
                result.append(tile_frame)

                tile_frame_count -= 1
            else:
                raise ValueError('ch: {}'.format(ch))

        return result
