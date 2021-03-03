# -*- coding: utf-8 -*-
from .gallery import Gallery
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.text import Label
from cocos.draw import Line
from model import Config
from math import trunc
from controller import events
from .button_gen import ButtonGen
from .display_interact_box import DisplayInteractBox
import random
from cocos.particle_systems import Sun
from cocos.particle import Color


class DisplayWorldmapCNC(Layer):
    """dashboard of the CNC"""
    display_pos_size = {"display_worldmap_cnc": {"X": 0, "Y": 0.248, "W":1, "H":0.7685}}
    button_positions = {"button_xo": {"X": 0.692, "Y": 0.0},
                        "display_interact_box_self": {"X": 0.74, "Y": -0.01},
                        "display_worldmap_hud_interact": {"X": 0.0, "Y": -0.2315},
                        "label_line_1": {"X": 0.22, "Y": -0.100, "fsize": 16},
                        "label_line_2": {"X": 0.22, "Y": -0.135, "fsize": 16},
                        "label_line_3": {"X": 0.22, "Y": -0.170, "fsize": 16},
                        "label_line_4": {"X": 0.22, "Y": -0.205, "fsize": 16},
                        "label_line_5": {"X": 0.22, "Y": -0.240, "fsize": 16},
                        "ps_alarm": {"X": 0.388, "Y": 0.758}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()
        self._load_interface()
        self.interact=False
        self.set_visibility(False)  
        self.alarm_status=False      

    def set_visibility(self, vis):        
        if vis:
            self.x=self.left_margin
        else:
            self.x=-self.optimal_width-self.left_margin
        if self.interact:
            self.remove_interact()
        self.visible=vis

    def refresh_labels(self):
        if self.alarm_status:
            if self.transarctica.proximity_alarm<1:
                self.remove("ps_alarm")
                self.alarm_status=False
        else:
            if self.transarctica.proximity_alarm>=1:
                if self.interact:
                    self.remove_interact()
                self.add(self.ps_alarm, name="ps_alarm")
                self.alarm_status=True

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["worldmap_cnc"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_worldmap_cnc"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_worldmap_cnc"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_worldmap_cnc"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        self.add(background)

        self.ps_alarm=Sun()
        self.ps_alarm.total_particles = 20
        self.ps_alarm.speed = 0.0
        self.ps_alarm.speed_var = 0.0
        self.ps_alarm.life_var = 0.0
        self.ps_alarm.blend_additive=True
        self.ps_alarm.position= (self.optimal_width * self.button_positions["ps_alarm"]["X"] + self.left_margin),(self.optimal_height * self.button_positions["ps_alarm"]["Y"] + self.bottom_margin) 
        self.ps_alarm.start_color = Color( 1, 0.40, 0.40, 0.40) 
        self.ps_alarm.size = 50.0

    def menu_xo(self):
        if not self.interact:
            background = Sprite(self.gallery.content["display"]["worldmap_hud_interact2"])
            background.image_anchor = 0, 0
            background.scale = self.optimal_scale
            background.x = 0
            background.y = 0
            self.add(background,name="display_worldmap_hud_interact")
            self.interact=True
            opt = {"0": {"text": "Prospect for coal", "param": "prospect"},
                   "1": {"text": "Deploy explosives", "param": "mine"},
                   "2": {"text": "Discuss", "param": "discuss_xo"},
                   "3": {"text": "That is all", "param": "end"}}

            display_interact_box_self=DisplayInteractBox(opt,"1",self.optimal_width * self.button_positions["display_interact_box_self"]["X"],self.optimal_width * self.button_positions["display_interact_box_self"]["Y"],self.optimal_scale)
            self.add(display_interact_box_self, name="display_interact_box_self")
            label_line_1 = self._load_label_gen("label_line_1")
            self.add(label_line_1, name="label_line_1")
            label_line_2 = self._load_label_gen("label_line_2")
            self.add(label_line_2, name="label_line_2")
            label_line_3 = self._load_label_gen("label_line_3")
            self.add(label_line_3, name="label_line_3")
            label_line_4 = self._load_label_gen("label_line_4")
            self.add(label_line_4, name="label_line_4")
            label_line_5 = self._load_label_gen("label_line_5")
            self.add(label_line_5, name="label_line_5")
            self.clear_text()
            self.get("label_line_1").element.text="Yes Conductor, how can I assist? "

    def clear_text(self):
        self.get("label_line_1").element.text=" "
        self.get("label_line_2").element.text=" "
        self.get("label_line_3").element.text=" "
        self.get("label_line_4").element.text=" "
        self.get("label_line_5").element.text=" "

    def remove_interact(self):
        self.remove("display_interact_box_self")
        self.remove("label_line_1")
        self.remove("label_line_2")
        self.remove("label_line_3")
        self.remove("label_line_4")
        self.remove("label_line_5")
        self.remove("display_worldmap_hud_interact")
        self.interact=False


    def discuss_with_xo(self):
        cok="N"
        while cok=="N":
            try:
                text=self.config.lang_file["discuss_xo_"+str(random.randint(0,10))]
                cok="Y"
            except:
                A=1
        for i in range(5, 0, -1):
            part = text.partition("#L"+str(i)+"#")      
            text = part[0]          
            self.get("label_line_"+str(i)).element.text=part[2]


    def _load_interface(self):
        self._load_button_gen("button", "xo", events.emit_menu_xo, "button_xo", 0, 1, 0.99)


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

