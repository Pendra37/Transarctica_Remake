# -*- coding: utf-8 -*-
from .gallery import Gallery
from .button_ligshovel import ButtonLigShovel
from .button_antshovel import ButtonAntShovel
from .button_speedregulator import ButtonSpeedRegulator
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.text import Label
from cocos.draw import Line
from model import Config
from math import trunc
from cocos.particle_systems import Fire
from cocos.particle_systems import Sun
from cocos.particle import Color


class DisplayWorldmapEngine(Layer):
    """dashboard of the engine"""
    display_pos_size = {"display_worldmap_engine": {"X": 0, "Y": 0.248, "W":1, "H":0.7685}}
    button_positions = {"button_antshovel": {"X": 0.50, "Y": 0.0},
                        "button_ligshovel": {"X": 0.20, "Y": 0.0},
                        "button_speedregulator": {"X": 0.574, "Y": 0.835},
                        "button_direction": {"X": 0.506, "Y": 0.09},
                        "button_break": {"X": 0.609, "Y": 0.09},
                        "ps_fire": {"X": 0.5, "Y": 0.08},
                        "pic_fire": {"X": 0.4233, "Y": 0.075},
                        "pic_anthracite": {"X": 0.65, "Y": 0.01},
                        "pic_lignite": {"X": 0.2, "Y": 0.01},
                        "label_speed_ind": {"X": 0.6395, "Y": 0.795, "fsize": 18.5},
                        "label_hpz_ind": {"X": 0.6395, "Y": 0.743, "fsize": 18.5},
                        "line_temp_ind": {"X": 0.682, "Y": 0.739, "EX": 0.682, "EY": 0.844},
                        "line_boiler_pressure_ind": {"X": 0.567, "Y": 0.740, "EX": 0.548, "EY": 0.787},
                        "ps_alarm": {"X": 0.535, "Y": 0.955}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()
        self._load_interface()
        self.set_visibility(False)  
        self.alarm_status=False      
        self.shovel_rate = {"Lignite": 0, "Anthracite": 0}

    def set_visibility(self, vis):        
        if vis:
            self.x=self.left_margin
        else:
            self.x=-self.optimal_width-self.left_margin
        self.visible=vis

    def refresh_labels(self):
        if self.alarm_status:
            if self.transarctica.proximity_alarm<1:
                self.remove("ps_alarm")
                self.alarm_status=False
        else:
            if self.transarctica.proximity_alarm>=1:
                self.add(self.ps_alarm, name="ps_alarm")
                self.alarm_status=True
 
        if self.shovel_rate["Anthracite"]!=self.transarctica.shovel_rate["Anthracite"]:
            if self.transarctica.shovel_rate["Anthracite"]==0:
                self.button_antshovel._reset_state()
            else:
                self.button_antshovel._update_state(1)
            self.shovel_rate["Anthracite"]=self.transarctica.shovel_rate["Anthracite"]
        if self.shovel_rate["Lignite"]!=self.transarctica.shovel_rate["Lignite"]:
            if self.transarctica.shovel_rate["Lignite"]==0:
                self.button_ligshovel._reset_state()
            else:
                self.button_ligshovel._update_state(1)
            self.shovel_rate["Lignite"]=self.transarctica.shovel_rate["Lignite"]
        if self.visible:
            self.label_hpz_ind.element.text = str(trunc(self.transarctica.hpz))
            self.label_speed_ind.element.text = str(trunc(self.transarctica.speed))
            
            y = self.optimal_height * self.button_positions["line_temp_ind"]["Y"] + self.bottom_margin
            ex = self.optimal_width * self.button_positions["line_temp_ind"]["EX"] + self.left_margin
            ey = self.optimal_height * self.button_positions["line_temp_ind"]["EY"] + self.bottom_margin
            self.line_temp_ind.end= (ex,trunc((ey - y) * self.transarctica.engine_temp / 600)+y)
            
            x = self.optimal_width * self.button_positions["line_boiler_pressure_ind"]["X"] + self.left_margin
            y = self.optimal_height * self.button_positions["line_boiler_pressure_ind"]["Y"] + self.bottom_margin
            ex = self.optimal_width * self.button_positions["line_boiler_pressure_ind"]["EX"] + self.left_margin
            ey = self.optimal_height * self.button_positions["line_boiler_pressure_ind"]["EY"] + self.bottom_margin
            self.line_boiler_pressure_ind.end= (trunc((x-ex) * 2 * self.transarctica.boiler_pressure / 110)+ex, ey)

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["worldmap_engine"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_worldmap_engine"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_worldmap_engine"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_worldmap_engine"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height

        pic_fire = Sprite(self.gallery.content["display"]["worldmap_engine_fire"])
        pic_fire.image_anchor = 0, 0
        pic_fire.scale = self.optimal_scale
        pic_fire.x = self.optimal_width * self.button_positions["pic_fire"]["X"] + self.left_margin
        pic_fire.y = self.optimal_height * self.button_positions["pic_fire"]["Y"]+ self.bottom_margin
        self.add(pic_fire, name="pic_fire")

        self.ps_fire=Fire()
        self.ps_fire.size=120
        self.ps_fire.position=(self.optimal_width * self.button_positions["ps_fire"]["X"] + self.left_margin, self.optimal_height * self.button_positions["ps_fire"]["Y"] + self.bottom_margin)
        self.add(self.ps_fire, name="ps_fire")

        self.add(background)

        pic_anthracite = Sprite(self.gallery.content["display"]["worldmap_engine_anthracite"])
        pic_anthracite.image_anchor = 0, 0
        pic_anthracite.scale = self.optimal_scale
        pic_anthracite.x = self.optimal_width * self.button_positions["pic_anthracite"]["X"] + self.left_margin
        pic_anthracite.y = self.optimal_height * self.button_positions["pic_anthracite"]["Y"]+ self.bottom_margin
        self.add(pic_anthracite, name="pic_anthracite")

        pic_lignite = Sprite(self.gallery.content["display"]["worldmap_engine_lignite"])
        pic_lignite.image_anchor = 0, 0
        pic_lignite.scale = self.optimal_scale
        pic_lignite.x = self.optimal_width * self.button_positions["pic_lignite"]["X"] + self.left_margin
        pic_lignite.y = self.optimal_height * self.button_positions["pic_lignite"]["Y"] + self.bottom_margin
        self.add(pic_lignite, name="pic_lignite")

        self.ps_alarm=Sun()
        self.ps_alarm.total_particles = 20
        self.ps_alarm.speed = 0.0
        self.ps_alarm.speed_var = 0.0
        self.ps_alarm.life_var = 0.0
        self.ps_alarm.blend_additive=True
        self.ps_alarm.position= (self.optimal_width * self.button_positions["ps_alarm"]["X"] + self.left_margin),(self.optimal_height * self.button_positions["ps_alarm"]["Y"] + self.bottom_margin) 
        self.ps_alarm.start_color = Color( 1, 0.40, 0.40, 0.40) 
        self.ps_alarm.size = 50.0


    def _load_interface(self):
        self._load_button_antshovel()
        self._load_button_ligshovel()
        self._load_button_speedregulator()
        self.label_hpz_ind = self._load_label_gen("label_hpz_ind")
        self.add(self.label_hpz_ind)
        self.label_speed_ind = self._load_label_gen("label_speed_ind")
        self.add(self.label_speed_ind)

        x = self.optimal_width * self.button_positions["line_temp_ind"]["X"] + self.left_margin
        y = self.optimal_height * self.button_positions["line_temp_ind"]["Y"] + self.bottom_margin
        ex = x
        ey = y
        self.line_temp_ind = Line((x,y), (ex,ey), (255, 0, 0, 255),2)
        self.add(self.line_temp_ind, name="line_temp_ind")

        x = self.optimal_width * self.button_positions["line_boiler_pressure_ind"]["X"] + self.left_margin
        y = self.optimal_height * self.button_positions["line_boiler_pressure_ind"]["Y"] + self.bottom_margin
        ex = self.optimal_width * self.button_positions["line_boiler_pressure_ind"]["EX"] + self.left_margin
        ey = self.optimal_height * self.button_positions["line_boiler_pressure_ind"]["EY"] + self.bottom_margin
        self.line_boiler_pressure_ind = Line((x,y), (ex,ey), (0, 0, 0, 255),2)
        self.add(self.line_boiler_pressure_ind, name="line_boiler_pressure_ind")


    def _load_button_antshovel(self):
        self.add(ButtonAntShovel(self.optimal_scale*1.4), name="button_antshovel")
        self.button_antshovel = self.children_names["button_antshovel"]
        self.button_antshovel.x = self.optimal_width * self.button_positions["button_antshovel"]["X"] + self.left_margin
        self.button_antshovel.y = self.optimal_height * self.button_positions["button_antshovel"]["Y"] + self.bottom_margin

    def _load_button_ligshovel(self):
        self.add(ButtonLigShovel(self.optimal_scale*1.4), name="button_ligshovel")
        self.button_ligshovel = self.children_names["button_ligshovel"]
        self.button_ligshovel.x = self.optimal_width * self.button_positions["button_ligshovel"]["X"] + self.left_margin
        self.button_ligshovel.y = self.optimal_height * self.button_positions["button_ligshovel"]["Y"] + self.bottom_margin

    def _load_button_speedregulator(self):
        self.add(ButtonSpeedRegulator(self.optimal_scale), name="button_speedregulator")
        button = self.children_names["button_speedregulator"]
        button.x = self.optimal_width * self.button_positions["button_speedregulator"]["X"] + self.left_margin
        button.y = self.optimal_height * self.button_positions["button_speedregulator"]["Y"] + self.bottom_margin
        knob_speedregulator = Sprite(self.gallery.content["knob"]["speedregulator"])
        knob_speedregulator.scale = self.optimal_scale
        x = self.optimal_width * self.button_positions["button_speedregulator"]["X"]
        y = self.optimal_height * self.button_positions["button_speedregulator"]["Y"]
        knob_speedregulator.x = x + self.left_margin + (button.width * 0.15)
        knob_speedregulator.y = y + self.bottom_margin + (button.height * 0.65)
        self.add(knob_speedregulator, name="knob_speedregulator")

    def move_speedregulator(self, Speed_Regulator):
        button_speedregulator=self.get("button_speedregulator")
        knob_speedregulator=self.get("knob_speedregulator")
        active_zone_width=button_speedregulator.width*0.8
        active_zone_height=button_speedregulator.height*0.55
        x=Speed_Regulator*active_zone_width
        y=(x-(active_zone_width/2))*(x-(active_zone_width/2))*(active_zone_height/((active_zone_width/2)*(active_zone_width/2))) - (active_zone_height/2)
        knob_speedregulator.x = x + button_speedregulator.x + (knob_speedregulator.width / 2)
        knob_speedregulator.y = y + button_speedregulator.y + (knob_speedregulator.height / 1.8)

    def _load_label_gen(self, obj_name):
        x = self.optimal_width * self.button_positions[obj_name]["X"] + self.left_margin
        y = self.optimal_height * self.button_positions[obj_name]["Y"] + self.bottom_margin
        fsize = round(self.optimal_scale * self.button_positions[obj_name]["fsize"])
        return Label("---", (x, y), color=(240,240,240,255), font_name="Arial", bold=True, font_size=fsize, anchor_x="right", anchor_y="center")
