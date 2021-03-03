# -*- coding: utf-8 -*-
from .gallery import Gallery
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from controller import events
from model import Config
from cocos.text import Label
from .button_gen import ButtonGen
import random

class DisplayCityTavern(Layer):
    display_pos_size = {"display_city_tavern": {"X": 0, "Y": 0.175, "W":1, "H":0.75}}
    button_positions = {"label_cityname": {"X": 0.5, "Y": 0.97},
                        "button_city_table": {"X": 0.0, "Y": 0.984},
                        "button_exit": {"X": 0.88, "Y": -0.16},
                        "button_talk": {"X": 0.78, "Y": -0.16},
                        "label_line_1": {"X": 0.055, "Y": -0.051, "fsize": 16},
                        "label_line_2": {"X": 0.055, "Y": -0.081, "fsize": 16},
                        "label_line_3": {"X": 0.055, "Y": -0.111, "fsize": 16},
                        "label_line_4": {"X": 0.055, "Y": -0.141, "fsize": 16},
                        "label_line_5": {"X": 0.055, "Y": -0.171, "fsize": 16}}

    #rumor_types={1 : "nothing", 2 : "coal_coordinate", 3 : "story", 4 : "nothing", 5 : "region", 6 : "herd", 7 : "trains"}
    rumor_types={1 : "nothing", 2 : "coal_coordinate", 3 : "story"}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()
        self._load_interface()
        self.set_visibility(False) 
        self.check_rumors()

    def set_visibility(self, vis):        
        if vis:
            self.x=self.left_margin
        else:
            self.x=-self.optimal_width-self.left_margin
        self.visible=vis

    def check_rumors(self):
        self.rumor_type=self.rumor_types[random.randint(1,len(self.rumor_types))]
        try:
            self.remove("button_talk")
        except:
            A=1
        if self.rumor_type=="nothing":
            self.get("label_line_1").element.text="Everyone is pretty quiet around."
        elif self.rumor_type=="coal_coordinate":
            self.get("label_line_1").element.text="Everyone is pretty quiet around."
            for coordinate in self.config.coal_mine:
                if not self.config.coal_mine[coordinate]["known"] and not self.config.coal_mine[coordinate]["mined"]:
                    self.get("label_line_1").element.text="Hey, Conductor, here, here. Need some coal? I have a coal mine coordinate for mere 100 baks."
                    self._load_button_gen("button", "talk", events.emit_tavern_talk, "button_talk", 0, 1, 0.95)
                    break
        elif self.rumor_type=="story":
            cok="N"
            while cok=="N":
                try:
                    text=self.config.lang_file["chatter_"+str(random.randint(0,10))]
                    cok="Y"
                except:
                    A=1
            for i in range(5, 0, -1):
                part = text.partition("#L"+str(i)+"#")      
                text = part[0]          
                self.get("label_line_"+str(i)).element.text=part[2]


    def tavern_talk(self):
        if self.rumor_type=="coal_coordinate":
            if self.transarctica.change_cargo_manifest("R",self.transarctica.get_item_id_from_name("Lignite"), 0, 100) == "Y":
                cnt=random.randint(1,40)
                while cnt>0:
                    for coordinate in self.config.coal_mine:
                        if not self.config.coal_mine[coordinate]["known"] and not self.config.coal_mine[coordinate]["mined"]:
                            cnt-=1
                            if cnt==0:
                                self.config.coal_mine[coordinate]["known"]=True
                                self.get("label_line_2").element.text=str(self.config.coal_mine[coordinate]["pos"])+"! This is all I heard."
                                self.remove("button_talk")
            else:
                self.get("label_line_2").element.text="That is not enough, no deal, now go away!"

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["city_tavern"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_city_tavern"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_city_tavern"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_city_tavern"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        self.add(background)

    def _load_interface(self):
        self._load_button_gen("button", "exit", events.emit_show_city_generic, "button_exit", 0, 1, 0.95)
        self._load_button_gen("display", "city_table", events.emit_return_to_map, "button_city_table", 0, 1, 1)
        self.label_cityname = Label(director.core.query_mover("Transarctica").in_city, (director.window.width * self.button_positions["label_cityname"]["X"], director.window.height*self.button_positions["label_cityname"]["Y"]), color=(210,200,128,255), font_name="Arial", bold=True, font_size=24, anchor_x="center", anchor_y="center")
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

