# -*- coding: utf-8 -*-
from .gallery import Gallery
from .button_gen import ButtonGen
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.text import Label
from model import Config
from math import trunc
from cocos.layer import ColorLayer
from controller import events

class DisplayCityHUD(Layer):
    """dashboard of the HUD"""
    display_pos_size = {"display_city_hud": {"X": 0, "Y": 0, "W":1, "H":0.1852}}
    button_positions = {}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()
        self._load_interface()

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["city_hud"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_city_hud"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_city_hud"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_city_hud"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        self.add(background)

    def _load_interface(self):
        a=1

    def _load_button_gen(self, gfx_type, gfx_name, event_name, obj_name, tag, scale, down_scale):
        self.add(ButtonGen(gfx_type, gfx_name, event_name, obj_name, tag, self.optimal_scale * scale, down_scale ), name=obj_name)
        button = self.children_names[obj_name]
        button.x = self.optimal_width * self.button_positions[obj_name]["X"] + self.left_margin
        button.y = self.optimal_height * self.button_positions[obj_name]["Y"] + self.bottom_margin 
