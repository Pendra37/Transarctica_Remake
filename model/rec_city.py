# -*- coding: utf-8 -*-


class RecCity(object):
    """model of a city"""
    valid_types = ["commercial", "industrial", "normal", "mammoth market", "service", "trainyard", "soldiers", "slaves", "viking"]

    def __init__(self, name, city_tile_x, city_tile_y, city_width, city_height, city_event_x, city_event_y, city_type, city_supply):
        """
        :param name: name of the city
        :param tile_x: X coordinate of the city's lower left tile
        :param tile_y: Y coordinate of the city's lower left tile
        :param width: width of the city in tiles
        :param height: height of the city in tiles
        :param event_x: X coordinate of the tile that bring up this city as an event
        :param event_y: Y  coordinate of the tile that bring up this city as an event
        :param city_type: must be one of the valid types
        :param supply: the item group the city is supplying
        """
        self.name = name
        self.tile_x = city_tile_x
        self.tile_y = city_tile_y
        self.width = city_width
        self.height = city_height
        self.event_x = city_event_x
        self.event_y = city_event_y
        #if city_type in self.valid_types:
        self.type = city_type
        self.supply = city_supply
        #else:
        #    raise ValueError
