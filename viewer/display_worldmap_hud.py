# -*- coding: utf-8 -*-
from .gallery import Gallery
#from .button_direction import ButtonDirection
from .button_gen import ButtonGen
from .display_worldmap_watch import DisplayWorldmapWatch
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.text import Label
from model import Config
from math import trunc
from cocos.layer import ColorLayer
from controller import events
from pyglet.media import load
from pyglet.media import Player, SourceGroup

class DisplayWorldmapHUD(Layer):
    """dashboard of the HUD"""
    display_pos_size = {"display_worldmap_hud": {"X": 0, "Y": 0, "W":1, "H":0.1852}}
    button_positions = {"button_engine": {"X": 0.215, "Y": 0.55},
                        "button_quarters": {"X": 0.33, "Y": 0.55},
                        "button_cnc": {"X": 0.215, "Y": 0.07},
                        "button_direction": {"X": 0.481, "Y": 0.07},
                        "button_break": {"X": 0.595, "Y": 0.07},
                        "button_minimap": {"X": 0.595, "Y": 0.55},
                        "button_find_engine": {"X": 0.481, "Y": 0.55},
                        "button_arrow_left": {"X": 0.0, "Y": 1.02},
                        "button_arrow_right": {"X": 0.986, "Y": 1.02},
                        "sprite_mini_train": {"X": 0.986, "Y": 1},
                        "label_liginite_ind": {"X": 0.816, "Y": 0.68, "fsize": 28},
                        "label_anthracit_ind": {"X": 0.895, "Y": 0.68, "fsize": 28},
                        "label_speed_ind": {"X": 0.950, "Y": 0.67, "fsize": 30},
                        "label_coordinates_ind": {"X": 0.875, "Y": 0.93, "fsize": 20}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()
        self._load_interface()
        self.switch_break()
        self.switch_direction()
        self.alarm_status=False      
        #self.alarm_sound = load('music/alarm.wav', streaming=False)
        #self.alarm_sound.volume=0.5 * self.config.sound_switch

    def refresh_labels(self,dt):
        self.get("clock").refresh_hand_positions(dt)
        self.label_liginite_ind.element.text = str(trunc(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]))
        self.label_anthracit_ind.element.text = str(trunc(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Anthracite")]["hold"]))
        self.label_speed_ind.element.text = str(trunc(self.transarctica.speed))
        self.label_coordinates_ind.element.text = str(self.transarctica.current_position["X"])+"/"+str(self.transarctica.current_position["Y"])
        if self.alarm_status:
            if self.transarctica.proximity_alarm<1:
                self.alarm_status=False
        else:
            if self.transarctica.proximity_alarm>=1:
                self.play_sound_once('music/alarm.wav',0.7) #alarm_sound.play()
                self.alarm_status=True

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["worldmap_hud"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_worldmap_hud"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_worldmap_hud"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_worldmap_hud"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        black_base = ColorLayer( 0,0,0,255, width=background.width, height=background.height)
        black_base.x = background.x 
        black_base.y = background.y 
        self.add(black_base)
        self._load_button_gen("button", "engine", events.emit_show_engine, "button_engine", 0, 1, 0.9)
        self._load_button_gen("button", "quarters", events.emit_show_quarters, "button_quarters", 0, 1, 0.9)
        self._load_button_gen("button", "cnc", events.emit_show_cnc, "button_cnc", 0, 1, 0.9)
        self._load_button_gen("button", "minimap", events.emit_show_minimap, "button_minimap", 0, 1, 0.9)
        self._load_button_gen("button", "find_engine", events.emit_find_engine, "button_find_engine", 0, 1, 0.9)
        self._load_button_gen("button", "arrow_left", events.emit_scroll_minitrain, "button_arrow_left", 0, 0.4, 0.95)
        self._load_button_gen("button", "arrow_right", events.emit_scroll_minitrain, "button_arrow_right", 0, 0.4, 0.95)
        #self._load_button_direction()
        self._load_button_gen("button", "break_on", events.emit_switch_break, "button_break", 0, 1, 0.95)
        self._load_button_gen("button", "direction_for", events.emit_switch_direction, "button_direction", 0, 1, 0.95)
        self.add(background)

    def _load_interface(self):
        self._load_clock()
        self.label_liginite_ind = self._load_label_gen("label_liginite_ind")
        self.add(self.label_liginite_ind)
        self.label_anthracit_ind = self._load_label_gen("label_anthracit_ind")
        self.add(self.label_anthracit_ind)
        self.label_speed_ind = self._load_label_gen("label_speed_ind")
        self.add(self.label_speed_ind)
        self.label_coordinates_ind = self._load_label_gen("label_coordinates_ind")
        self.add(self.label_coordinates_ind)

    def _load_clock(self):
        self.add(DisplayWorldmapWatch(self.config.start_timestamp), z=len(self.children), name="clock")
        clock = self.children_names["clock"]
        clock.scale = self.optimal_scale
        padding = (self.config.window_width - self.optimal_width) / 2
        clock.x += padding

    def play_sound_once(self,soundfile,volume):
        if self.config.sound_switch>0:
            play_sound = Player()
            play_sound_source = load(soundfile)
            play_sound_group = SourceGroup(play_sound_source.audio_format, None)
            play_sound_group.loop = False
            play_sound_group.queue(play_sound_source)
            play_sound.queue(play_sound_group)
            play_sound.volume=float(volume) * self.config.sound_switch
            play_sound.play()

    def _load_button_gen(self, gfx_type, gfx_name, event_name, obj_name, tag, scale, down_scale):
        self.add(ButtonGen(gfx_type, gfx_name, event_name, obj_name, tag, self.optimal_scale * scale, down_scale ), name=obj_name)
        button = self.children_names[obj_name]
        button.x = self.optimal_width * self.button_positions[obj_name]["X"]
        button.y = self.optimal_height * self.button_positions[obj_name]["Y"]

    def _load_label_gen(self, obj_name):
        x = self.optimal_width * self.button_positions[obj_name]["X"]
        y = self.optimal_height * self.button_positions[obj_name]["Y"]
        fsize = round(self.optimal_scale * self.button_positions[obj_name]["fsize"])
        return Label("---", (x, y), color=(210,200,128,255), font_name="Arial", bold=True, font_size=fsize, anchor_x="right", anchor_y="center")

    def _load_button_direction(self):
        self.add(ButtonDirection(self.optimal_scale), name="button_direction")
        self.button_direction = self.children_names["button_direction"]
        self.button_direction.x = self.optimal_width * self.button_positions["button_direction"]["X"]
        self.button_direction.y = self.optimal_height * self.button_positions["button_direction"]["Y"]


    def switch_break(self):
        if self.transarctica.is_break_released:
            self.get("button_break").sprite.image=self.gallery.content["button"]["break_off"]
        else:
            self.get("button_break").sprite.image=self.gallery.content["button"]["break_on"]

    def switch_direction(self):
        if self.transarctica.is_in_reverse:
            self.get("button_direction").sprite.image=self.gallery.content["button"]["direction_rev"]
        else:
            self.get("button_direction").sprite.image=self.gallery.content["button"]["direction_for"]






