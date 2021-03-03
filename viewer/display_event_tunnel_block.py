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
from math import trunc
import random

class DisplayEventTunnelBlock(Layer):
    display_pos_size = {"display_event_tunnel_block": {"X": 0, "Y": 0.175, "W":1, "H":0.75}}
    button_positions = {"label_cityname": {"X": 0.5, "Y": 0.97},
                        "button_city_table": {"X": 0.0, "Y": 0.984},
                        "button_exit": {"X": 0.88, "Y": -0.16},
                        "label_line_1": {"X": 0.055, "Y": -0.051, "fsize": 16},
                        "label_line_2": {"X": 0.055, "Y": -0.081, "fsize": 16},
                        "label_line_3": {"X": 0.055, "Y": -0.111, "fsize": 16},
                        "label_line_4": {"X": 0.055, "Y": -0.141, "fsize": 16},
                        "label_line_5": {"X": 0.055, "Y": -0.171, "fsize": 16}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()
        self._load_interface()
        self.set_visibility(False)

    def set_visibility(self, vis):        
        if vis:
            self.x=self.left_margin
            self.update_desc()
        else:
            self.x=-self.optimal_width-self.left_margin
        self.visible=vis


    def set_visibility(self, vis):        
        if vis:
            self.x=self.left_margin
            self.do_engagement()
        else:
            self.x=-self.optimal_width-self.left_margin
        self.visible=vis

    def do_engagement(self):
        self.transarctica_force=self.transarctica.calculate_force_value("short_range")
        self.molemen_force=random.randint(self.config.molemen_force["min"], self.config.molemen_force["max"])
        self.loot_perc=trunc(max(0,(1-self.transarctica_force/max(1,self.molemen_force)))*(self.config.molemen_loot["max"]-self.config.molemen_loot["min"])+self.config.molemen_loot["min"])
        message=self.transarctica.calculate_loot_loss("molemen", self.loot_perc)
        self.get("label_line_1").element.text="Your force: "+str(self.transarctica_force) + " vs Mole men force: "+str(self.molemen_force)
        loss_list=message+" Losses: "
        line=2
        for item_id in self.transarctica.cargo_manifest:
            if self.transarctica.cargo_manifest[item_id]["loss"]>0:
                loss_list+=self.config.conf_items[item_id].screen_name+": "+str(self.transarctica.cargo_manifest[item_id]["loss"])+", "
                if len(loss_list)>90:
                    self.get("label_line_"+str(min(4,line))).element.text=loss_list
                    loss_list=""
                    line+=1
        self.get("label_line_"+str(min(4,line))).element.text=loss_list

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["event_tunnel_block"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_event_tunnel_block"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_event_tunnel_block"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_event_tunnel_block"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        self.add(background)

    def _load_interface(self):
        self._load_button_gen("button", "exit", events.emit_return_to_map, "button_exit", 0, 1, 0.95)
        self._load_button_gen("display", "city_table", events.emit_return_to_map, "button_city_table", 0, 1, 1)
        self.label_cityname = Label("Mole Men Ambush!", (director.window.width * self.button_positions["label_cityname"]["X"], director.window.height*self.button_positions["label_cityname"]["Y"]), color=(210,200,128,255), font_name="Arial", bold=True, font_size=24, anchor_x="center", anchor_y="center")
        self.add(self.label_cityname)
        label_line_1 = self._load_label_gen("label_line_1")
        self.add(label_line_1, name="label_line_1")
        self.get("label_line_1").element.text=" "
        label_line_2 = self._load_label_gen("label_line_2")
        self.add(label_line_2, name="label_line_2")
        self.get("label_line_2").element.text=" "
        label_line_3 = self._load_label_gen("label_line_3")
        self.add(label_line_3, name="label_line_3")
        self.get("label_line_3").element.text=" "
        label_line_4 = self._load_label_gen("label_line_4")
        self.add(label_line_4, name="label_line_4")
        self.get("label_line_4").element.text=" "
        label_line_5 = self._load_label_gen("label_line_5")
        self.add(label_line_5, name="label_line_5")
        self.get("label_line_5").element.text=" "

    def _load_label_gen(self, obj_name):
        x = self.optimal_width * self.button_positions[obj_name]["X"] + self.left_margin
        y = self.optimal_height * self.button_positions[obj_name]["Y"] + self.bottom_margin
        fsize = round(self.optimal_scale * self.button_positions[obj_name]["fsize"])
        return Label("---", (x, y), color=(210,200,128,255), font_name="Arial", bold=True, font_size=fsize, anchor_x="left", anchor_y="center")

    def _load_button_gen(self, gfx_type, gfx_name, event_name, obj_name, tag, scale, down_scale):
        self.add(ButtonGen(gfx_type, gfx_name, event_name, obj_name, tag, self.optimal_scale * scale, down_scale ), name=obj_name)
        button = self.children_names[obj_name]
        button.x = self.optimal_width * self.button_positions[obj_name]["X"] + self.left_margin
        button.y = self.optimal_height * self.button_positions[obj_name]["Y"] + self.bottom_margin 
