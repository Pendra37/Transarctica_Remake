# -*- coding: utf-8 -*-
from . import Config, Transarctica, VUTrain, Roamer

class Game(object):
    """represents a loadable instance of the game"""
    def __init__(self, game_name):
        """initializer"""
        self._game_name = game_name
        self.config = Config()
        self.map_file = self.get_map_file_name()
        self.world_objects = {}
        self.world_objects["trains"] = {}
        self.world_objects["trains"]["Transarctica"] = Transarctica()
        for id in range(self.config.vutrain_count):
            self.world_objects["trains"]["VUTrain"+str(id)] = VUTrain()
        for id in range(self.config.roamer_count):
            self.world_objects["trains"]["Roamer"+str(id)] = Roamer()


    def get_map_file_name(self):
        return "{}/{}.{}".format(self.config.resources, self._game_name, self.config.map_format)

    def query_mover(self, actor_name):
        return self.world_objects["trains"][actor_name]
