# -*- coding: utf-8 -*-
from model import Config
from cocos.director import director
import random

class Roamer(object):
    """Roamers, mammoth_herd 0, nomads 1, raiders 2"""
    directions = ["N", "B", "E", "C", "S", "D", "W", "A"]

    def __init__(self):
        """initilaizer"""
        self.config = Config()
        self.is_break_released = True
        self.train_layout = {}  
        self.cargo_manifest = {} 
        self.current_position = {"X": 15, "Y": 9}
        self.current_position["X"] = random.randint(5, self.config.map_width-5)
        self.current_position["Y"] = random.randint(5, self.config.map_height-5)
        self.roamer_type=self.config.roamer_types[random.randint(0, len(self.config.roamer_types)-1)]  
        self.speed=random.randint(30, 60)
        self.direction = "W"
        self.force_rating=random.randint(60, 280)

    def game_loaded(self, game_object):
        self.direction = game_object["direction"]
        self.is_break_released = game_object["is_break_released"]
        self.speed = game_object["speed"]
        self.current_position = game_object["current_position"]
        self.roamer_type=game_object["roamer_type"]
        self.force_rating=game_object["force_rating"]

    def current_timestamp(self):
        return director.core.timestamp