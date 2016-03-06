"""
xTile graphics type readers
"""

from __future__ import print_function

from xnb_parse.type_reader import (TypeReaderPlugin, BaseTypeReader, ValueTypeReader, GenericTypeReader,
                                   generic_reader_type)
from xnb_parse.xna_types.xTile.xTile_graphics import (Map, TileSheet, Size, Layer, Tile)

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

            id_ = self.stream.read_long_string()
            description = self.stream.read_long_string()
            properties = self.read_properties()
            tilesheets = self.read_tilesheets()
            layers = self.read_layers()

            return Map(id_, description, properties, tilesheets, layers)
        else:
            raise NotImplementedError('Only windows support at this moment')

    def read_properties(self):
        if self.file_platform == PLATFORM_WINDOWS:
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
        else:
            raise NotImplementedError('Only windows support at this moment')

    def read_tilesheets(self):
        if self.file_platform == PLATFORM_WINDOWS:
            tilesheet_count = self.stream.read_int32()

            result = []
            for i in range(tilesheet_count):
                id_ = self.stream.read_long_string()
                description = self.stream.read_long_string()
                image_source = self.stream.read_long_string()
                sheet_size = self.read_size()
                tile_size = self.read_size()
                margin = self.read_size()
                spacing = self.read_size()
                properties = self.read_properties()

                tilesheet = TileSheet(id_, description, image_source, sheet_size, tile_size, margin, spacing, properties)
                result.append(tilesheet)

            return result
        else:
            raise NotImplementedError('Only windows support at this moment')

    def read_size(self):
        if self.file_platform == PLATFORM_WINDOWS:
            width = self.stream.read_int32()
            height = self.stream.read_int32()

            return Size(width, height)
        else:
            raise NotImplementedError('Only windows support at this moment')

    def read_layers(self):
        if self.file_platform == PLATFORM_WINDOWS:
            layers_count = self.stream.read_int32()

            result = []
            for i in range(layers_count):
                id_ = self.stream.read_long_string()
                visible = self.stream.read_boolean()
                description = self.stream.read_long_string()
                layer_size = self.read_size()
                tile_size = self.read_size()
                properties = self.read_properties()
                tiles = self.read_tiles(layer_size)

                tilesheet = Layer(id_, visible, description, layer_size, tile_size, properties, tiles)
                result.append(tilesheet)

            return result
        else:
            raise NotImplementedError('Only windows support at this moment')

    def read_tiles(self, layer_size):
        result = []
        for current_y in range(layer_size.height):
            current_x = 0
            while current_x < layer_size.width:
                ch = self.stream.read_char()
                if ch == 'T':  # tilesheet id
                    tilesheet_id = self.stream.read_long_string()

                elif ch == 'N':  # nulls
                    null_count = self.stream.read_int32()
                    current_x += null_count

                elif ch == 'S':  # static tile
                    tile_index = self.stream.read_int32()
                    blend_mode = self.stream.read_7bit_encoded_int()  # enum(Alpha, Additive)
                    properties = self.read_properties()
                    x = current_x
                    y = current_y

                    if tilesheet_id is None:
                        raise ValueError('tilesheet_id')

                    tile = Tile(tile_index, blend_mode, properties, x, y, tilesheet_id)

                    result.append(tile)
                    current_x += 1

                elif ch == 'A':  # animated tile
                    raise NotImplementedError('')  # TODO: do not forget

        return result
