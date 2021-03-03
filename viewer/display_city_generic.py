# -*- coding: utf-8 -*-
from .gallery import Gallery
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from controller import events
from model import Config
from cocos.text import Label
from .button_gen import ButtonGen
from controller import events

class DisplayCityGeneric(Layer):
    """shows a background image of the city"""
    display_pos_size = {"display_city_generic": {"X": 0, "Y": 0.175, "W":1, "H":0.75}}
    button_positions = {"label_cityname": {"X": 0.5, "Y": 0.970},
                        "button_city_table": {"X": 0.0, "Y": 0.984},
                        "button_city_commerce": {"X": 0.215, "Y": 0.606},
                        "button_city_tavern": {"X": 0.4436, "Y": 0.639},
                        "button_city_barracks": {"X": 0.663, "Y": 0.0},
                        "button_city_special": {"X": 0, "Y": 0.479},
                        "button_city_leave": {"X": 0.4885, "Y": 0.198}}


    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()
        self._load_interface()
        self.set_visibility(True)
 

    def set_visibility(self, vis):        
        if vis:
            self.x=self.left_margin
        else:
            self.x=-self.optimal_width-self.left_margin
        self.visible=vis

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["city_generic"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_city_generic"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_city_generic"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_city_generic"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        self.add(background)

    def _load_interface(self):
        self._load_button_gen("button", "city_commerce", events.emit_show_city_commerce, "button_city_commerce", 0, 1, 0.99)
        self._load_button_gen("button", "city_tavern", events.emit_show_city_tavern, "button_city_tavern", 0, 1, 0.99)
        #self._load_button_gen("button", "city_barracks", events.emit_show_city_barracks, "button_city_barracks", 0, 1, 0.99)
        self._load_button_gen("button", "city_special", events.emit_show_city_special, "button_city_special", 0, 1, 0.99)
        self._load_button_gen("button", "city_leave", events.emit_return_to_map, "button_city_leave", 0, 1, 0.99)
        self._load_button_gen("display", "city_table", events.emit_return_to_map, "button_city_table", 0, 1, 1)
        self.label_cityname = Label(director.core.query_mover("Transarctica").in_city, (director.window.width * self.button_positions["label_cityname"]["X"], director.window.height*self.button_positions["label_cityname"]["Y"]), color=(210,200,128,255), font_name="Arial", bold=True, font_size=24, anchor_x="center", anchor_y="center")
        self.add(self.label_cityname)

    def _load_button_gen(self, gfx_type, gfx_name, event_name, obj_name, tag, scale, down_scale):
        self.add(ButtonGen(gfx_type, gfx_name, event_name, obj_name, tag, self.optimal_scale * scale, down_scale ), name=obj_name)
        button = self.children_names[obj_name]
        button.x = self.optimal_width * self.button_positions[obj_name]["X"] + self.left_margin
        button.y = self.optimal_height * self.button_positions[obj_name]["Y"] + self.bottom_margin 

