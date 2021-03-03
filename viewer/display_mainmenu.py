# -*- coding: utf-8 -*-
from .gallery import Gallery
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.text import Label
from controller import events
from model import Config
from .button_gen import ButtonGen
from model import Config

class DisplayMainMenu(Layer):
    display_pos_size = {"display_mainmenu": {"X": 0, "Y": -0.03, "W":1, "H":1}}
    button_positions = {"display_mainmenu_hud": {"X": 0.0, "Y": 0.0},
                        "button_startgame": {"X": 0.4661, "Y": 0.039},
                        "button_sound_switch": {"X": 0.866, "Y": 0.035},
                        "button_loadgame": {"X": 0.661, "Y": 0.035},
                        "button_quickbattle": {"X": 0.261, "Y": 0.035}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.sound_on_off='on'
        self._load_background()
        self._load_interface()

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["mainmenu"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_mainmenu"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_mainmenu"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_mainmenu"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        self.add(background)

    def _load_interface(self):
        hud = Sprite(self.gallery.content["display"]["mainmenu_hud"])
        hud.image_anchor = 0, 0
        hud.scale = self.optimal_scale
        hud.x = 0
        hud.y = 0
        self.add(hud)

        self._load_button_gen("button", "startgame", events.emit_start_game, "button_startgame", 0, 0.4, 0.95)
        self._load_button_gen("button", "loadgame", events.emit_load_game, "button_loadgame", 0, 0.4, 0.95)
        self._load_button_gen("button", "sound_"+self.sound_on_off, events.emit_sound_switch, "button_sound_switch", 0, 0.4, 0.95)
        self._load_button_gen("button", "startgame", events.emit_quick_battle, "button_quickbattle", 0, 0.4, 0.95)

    def switch_sound(self):
        if self.sound_on_off=='on':
            self.sound_on_off='off'
        else:
            self.sound_on_off='on'
        self.get("button_sound_switch").sprite.image=self.gallery.content["button"]["sound_"+self.sound_on_off]


    def _load_button_gen(self, gfx_type, gfx_name, event_name, obj_name, tag, scale, down_scale):
        self.add(ButtonGen(gfx_type, gfx_name, event_name, obj_name, tag, self.optimal_scale * scale, down_scale ), name=obj_name)
        button = self.children_names[obj_name]
        button.x = self.optimal_width * self.button_positions[obj_name]["X"]
        button.y = self.optimal_height * self.button_positions[obj_name]["Y"]

