# -*- coding: utf-8 -*-
from .gallery import Gallery
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from model import Config
from math import trunc
from cocos.layer import ColorLayer
from controller import events
from cocos.text import Label, HTMLLabel, RichLabel
from .button_gen import ButtonGen
from .display_interact_box import DisplayInteractBox
import random
from cocos.particle_systems import Sun
from cocos.particle import Color


class DisplayWorldmapQuarters(Layer):
    """dashboard of the quarters"""
    display_pos_size = {"display_worldmap_quarters": {"X": 0, "Y": 0.248, "W":1, "H":0.7685}}
    button_positions = {"button_adjutant": {"X": 0.1726, "Y": 0.0},
                        "button_save": {"X": 0.598, "Y": 0.003},
                        "button_pistol": {"X": 0.495, "Y": 0.07},
                        "display_interact_box_self": {"X": 0.74, "Y": -0.01},
                        "display_worldmap_hud_interact": {"X": 0.0, "Y": -0.2315},
                        "label_line_1": {"X": 0.22, "Y": -0.100, "fsize": 16},
                        "label_line_2": {"X": 0.22, "Y": -0.135, "fsize": 16},
                        "label_line_3": {"X": 0.22, "Y": -0.170, "fsize": 16},
                        "label_line_4": {"X": 0.22, "Y": -0.205, "fsize": 16},
                        "label_line_5": {"X": 0.22, "Y": -0.240, "fsize": 16},
                        "inventory_margain": {"X": 0.0, "Y": 0.0},
                        "ps_alarm": {"X": 0.2325, "Y": 0.8035}}

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
        background = Sprite(self.gallery.content["display"]["worldmap_quarters"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_worldmap_quarters"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_worldmap_quarters"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_worldmap_quarters"]["Y"]
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



    def _load_interface(self):
        self._load_button_gen("button", "adjutant", events.emit_menu_adjutant, "button_adjutant", 0, 1, 0.99)
        self._load_button_gen("button", "save", events.emit_save, "button_save", 0, 1, 0.99)
        self._load_button_gen("button", "pistol", events.emit_save, "button_pistol", 0, 1, 0.99)

    def menu_adjutant(self):
        if not self.interact:
            background = Sprite(self.gallery.content["display"]["worldmap_hud_interact2"])
            background.image_anchor = 0, 0
            background.scale = self.optimal_scale
            background.x = 0
            background.y = 0
            self.add(background,name="display_worldmap_hud_interact")
            self.interact=True
            opt = {"0": {"text": "Current inventory", "param": "inventory"},
                   "1": {"text": "Discuss", "param": "discuss_adjutant"},
                   "2": {"text": "That is all", "param": "end"}}

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
        try:
            self.close_inventory()
        except:
            A=1



    def discuss_with_adjutant(self):
        cok="N"
        while cok=="N":
            try:
                text=self.config.lang_file["discuss_adjutant_"+str(random.randint(0,10))]
                cok="Y"
            except:
                A=1
        for i in range(5, 0, -1):
            part = text.partition("#L"+str(i)+"#")      
            text = part[0]          
            self.get("label_line_"+str(i)).element.text=part[2]

    def show_inventory(self):
        self._load_button_gen("display", "inventory", events.emit_close_inventory, "inventory_margain", 0, 1, 1)
        eol="                                                                                                          "
        
        desctext="{font_size 22}Cargo manifest"+eol
        for item_id in self.transarctica.cargo_manifest:
            if (self.transarctica.cargo_manifest[item_id]["hold"]>0) :
                desctext+="{font_size 14}"+self.config.conf_items[item_id].item_name+", holds: "+str(self.transarctica.cargo_manifest[item_id]["hold"])+eol
        label_desc = RichLabel(desctext, multiline=True, font_name="Arial", x=650, y=830, width=400, color=(210,200,128,255), anchor_x="left", anchor_y="top")
        self.add(label_desc, name="text_cargo") 
        cnt=0
        desctext=""
        for wagon_id in range(self.config.base_wagon_range): #self.config.conf_wagons:
            wagon_count = self.transarctica.count_wagon_with_id(wagon_id)
            if wagon_count>0:
                desctext+="{font_size 14}"+self.config.conf_wagons[wagon_id].wagon_name+": "+str(wagon_count)+eol
                cnt+=wagon_count
        desctext="{font_size 14}Number of wagons: "+str(cnt)+eol+desctext
        desctext="{font_size 22}Wagon list"+eol+desctext
        label_desc = RichLabel(desctext, multiline=True, font_name="Arial", x=375, y=830, width=400, color=(210,200,128,255), anchor_x="left", anchor_y="top")
        self.add(label_desc, name="text_wagons") 

        desctext="{font_size 22}Generic stats"+eol
        train_weight=self.transarctica.calculate_wagon_weight()
        cargo_weight=self.transarctica.calculate_cargo_weight()
        desctext+="{font_size 14}Train weight: "+str(train_weight)+eol
        desctext+="{font_size 14}Cargo weight: "+str(cargo_weight)+eol
        desctext+="{font_size 14}Total weight: "+str(train_weight+cargo_weight)+eol
        for storage_type in self.transarctica.storage_cap:
            if self.transarctica.storage_cap[storage_type]["max"]>0: 
                desctext+=storage_type+": "+str(self.transarctica.storage_cap[storage_type]["current"])+"/"+str(self.transarctica.storage_cap[storage_type]["max"])+eol
        label_desc = RichLabel(desctext, multiline=True, font_name="Arial", x=100, y=830, width=400, color=(210,200,128,255), anchor_x="left", anchor_y="top")
        self.add(label_desc, name="text_generic") 

        desctext="{font_size 22}Notes"+eol
        desctext+="{font_size 14}Coal mine coordinates: "
        for coordinate in self.config.coal_mine:
            if self.config.coal_mine[coordinate]["known"] and not self.config.coal_mine[coordinate]["mined"]:
                desctext+=self.config.coal_mine[coordinate]["pos"]+", "
        desctext=desctext[:len(desctext)-2]
        desctext+=eol
        label_desc = RichLabel(desctext, multiline=True, font_name="Arial", x=950, y=830, width=600, color=(210,200,128,255), anchor_x="left", anchor_y="top")
        self.add(label_desc, name="text_notes") 


    def close_inventory(self):
        self.remove("inventory_margain")
        self.remove("text_cargo")
        self.remove("text_wagons")
        self.remove("text_generic")
        self.remove("text_notes")

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
