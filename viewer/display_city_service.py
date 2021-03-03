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
from cocos.layer import ColorLayer

class DisplayCityService(Layer):
    display_pos_size = {"display_city_service": {"X": 0, "Y": 0.175, "W":1, "H":0.75}}
    button_positions = {"label_cityname": {"X": 0.5, "Y": 0.97},
                        "button_city_table": {"X": 0.0, "Y": 0.984},
                        "button_exit": {"X": 0.88, "Y": -0.16},
                        "button_service_switch_wagons": {"X": 0.0, "Y": 0.0},
                        "button_service_repair_wagons": {"X": 0.23, "Y": 0.0},
                        "label_line_4": {"X": 0.055, "Y": -0.141, "fsize": 16},
                        "label_line_5": {"X": 0.055, "Y": -0.171, "fsize": 16}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()
        self.service_mode="NA"
        self.elements_to_remove=[]
        self._load_interface()
        self.set_visibility(True) 
        self.TA = -1

    def set_visibility(self, vis):        
        if vis:
            self.x=self.left_margin
        else:
            self.x=-self.optimal_width-self.left_margin
        self.visible=vis

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["city_service"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_city_service"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_city_service"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_city_service"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        self.add(background)

    def _load_interface(self):
        self._load_button_gen("button", "exit", events.emit_return_to_map, "button_exit", 0, 1, 0.95)
        self._load_button_gen("button", "service_switch_wagons", events.emit_service_switch_wagons, "button_service_switch_wagons", 0, 1, 0.95)
        self._load_button_gen("button", "service_repair_wagons", events.emit_service_repair_wagons, "button_service_repair_wagons", 0, 1, 0.95)
        self._load_button_gen("display", "city_table", events.emit_return_to_map, "button_city_table", 0, 1, 1)
        self.label_cityname = Label(director.core.query_mover("Transarctica").in_city, (director.window.width * self.button_positions["label_cityname"]["X"], director.window.height*self.button_positions["label_cityname"]["Y"]), color=(210,200,128,255), font_name="Arial", bold=True, font_size=24, anchor_x="center", anchor_y="center")
        self.add(self.label_cityname)
        label_line_4 = self._load_label_gen("label_line_4")
        self.add(label_line_4, name="label_line_4")
        self.get("label_line_4").element.text=" "
        label_line_5 = self._load_label_gen("label_line_5")
        self.add(label_line_5, name="label_line_5")
        self.get("label_line_5").element.text=" "

        self.draw_wagons_buttons()

    def remove_wagon_buttons(self):
        for obj in self.elements_to_remove:
            self.remove(obj)
        self.elements_to_remove.clear()   

    def set_service_mode(self, action):
        self.service_mode=action
        self.TA=-1
        self.remove_wagon_buttons()
        self.draw_wagons_buttons()

    def draw_wagons_buttons(self):
        if self.service_mode=="R":
            self.get("label_line_4").element.text="Select wagon to Repair."+"You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"
        elif self.service_mode=="S":
            self.get("label_line_4").element.text="Select wagons to Switch."+"You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"
        wagon_scale=0.30
        right_pad=self.config.window_width*0.85
        curr_x=right_pad
        curr_y=self.optimal_height*0.15
        train = Sprite(self.gallery.content["wagon"]["blank"])
        train.scale = self.optimal_scale*wagon_scale
        divider = train.width
        if self.service_mode=="S":
            self._load_button_gen("wagon", "blank", events.emit_wagon_service, "button_wagon_b"+str(0), 100, wagon_scale, 0.95,curr_x,curr_y)
            self.elements_to_remove.append("button_wagon_b"+str(0))
            for wg in self.transarctica.train_layout:
                train = Sprite(self.gallery.content["wagon"][self.config.conf_wagons[self.transarctica.train_layout[wg]].display_image])
                train.image_anchor = 0, 0
                train.scale = self.optimal_scale*wagon_scale
                curr_x = curr_x-train.width
                if curr_x <= 50:  
                    right_pad -= self.config.window_width*0.05
                    curr_x = right_pad-train.width
                    curr_y -= self.optimal_height*0.05
                train.x = curr_x
                train.y = curr_y
                self._load_button_gen("wagon", self.config.conf_wagons[self.transarctica.train_layout[wg]].display_image, events.emit_wagon_service, "button_wagon_"+str(wg), wg, wagon_scale, 0.95,curr_x,curr_y)
                self.elements_to_remove.append("button_wagon_"+str(wg))
                if int(self.config.conf_wagons[self.transarctica.train_layout[wg]].damage)>0:
                    damage_base = ColorLayer( 255,0,0,255, width=trunc((train.width/4)*(4-int(self.config.conf_wagons[self.transarctica.train_layout[wg]].damage))), height=train.height//10)
                    damage_base.x = train.x
                    damage_base.y = train.y+damage_base.height*9
                    self.add(damage_base, name="healthbar_wagon_"+str(wg))
                    self.elements_to_remove.append("healthbar_wagon_"+str(wg))
                curr_x = curr_x-divider
                self._load_button_gen("wagon", "blank", events.emit_wagon_service, "button_wagon_b"+str(wg+1), 101+wg, wagon_scale, 0.95,curr_x,curr_y)
                self.elements_to_remove.append("button_wagon_b"+str(wg+1))
        if self.service_mode=="R":
            for wg in self.transarctica.train_layout:
                if self.config.conf_wagons[self.transarctica.train_layout[wg]].damage>0: 
                    train = Sprite(self.gallery.content["wagon"][self.config.conf_wagons[self.transarctica.train_layout[wg]].display_image])
                    train.image_anchor = 0, 0
                    train.scale = self.optimal_scale*wagon_scale
                    curr_x = curr_x-train.width
                    if curr_x <= 50:  
                        right_pad -= self.config.window_width*0.05
                        curr_x = right_pad-train.width
                        curr_y -= self.optimal_height*0.05
                    train.x = curr_x
                    train.y = curr_y
                    self._load_button_gen("wagon", self.config.conf_wagons[self.transarctica.train_layout[wg]].display_image, events.emit_wagon_service, "button_wagon_"+str(wg), wg, wagon_scale, 0.95,curr_x,curr_y)
                    self.elements_to_remove.append("button_wagon_"+str(wg))
                    if int(self.config.conf_wagons[self.transarctica.train_layout[wg]].damage)>0:
                        damage_base = ColorLayer( 255,0,0,255, width=trunc((train.width/4)*(4-int(self.config.conf_wagons[self.transarctica.train_layout[wg]].damage))), height=train.height//10)
                        damage_base.x = train.x
                        damage_base.y = train.y+damage_base.height*9
                        self.add(damage_base, name="healthbar_wagon_"+str(wg))
                        self.elements_to_remove.append("healthbar_wagon_"+str(wg))


    def do_transaction(self, Action, tag):
        tag_val=int(tag)
        if Action=="NA": 
            if self.service_mode=="S":
                if self.TA==tag_val:
                    self.TA=-1
                    self.get("label_line_4").element.text="You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"
                else:
                    if self.TA >= 0 and (self.TA<100 or tag_val<100):
                        self.transarctica.change_train_layout("M", self.TA, 15, 1, tag_val)
                        self.TA=-1
                        self.remove_wagon_buttons()
                        self.draw_wagons_buttons()
                    else:
                        self.TA=tag_val
                        extra_text="Change position: 15 baks. "
                        self.get("label_line_4").element.text=extra_text+"You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"
            elif self.service_mode=="R":
                if self.TA >= 0 and self.TA==tag_val:
                    self.get("label_line_4").element.text="You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"
                    repair_cost= trunc((int(self.config.conf_wagons[self.transarctica.train_layout[tag_val]].avg_price)/3)*int(self.config.conf_wagons[self.transarctica.train_layout[tag_val]].damage))
                    self.transarctica.change_train_layout("F", tag_val, repair_cost, 1, -1)
                    self.TA=-1
                    self.remove_wagon_buttons()
                    self.draw_wagons_buttons()
                else:
                    self.TA=tag_val
                    repair_cost= trunc((int(self.config.conf_wagons[self.transarctica.train_layout[tag_val]].avg_price)/3)*int(self.config.conf_wagons[self.transarctica.train_layout[tag_val]].damage))
                    extra_text="Repair cost: "+str(repair_cost)+" baks. Click on the wagon to proceed. "
                    self.get("label_line_4").element.text=extra_text+"You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"


    def _load_label_gen(self, obj_name):
        x = self.optimal_width * self.button_positions[obj_name]["X"] + self.left_margin
        y = self.optimal_height * self.button_positions[obj_name]["Y"] + self.bottom_margin
        fsize = round(self.optimal_scale * self.button_positions[obj_name]["fsize"])
        return Label("---", (x, y), color=(210,200,128,255), font_name="Arial", bold=True, font_size=fsize, anchor_x="left", anchor_y="center")

    def _load_button_gen(self, gfx_type, gfx_name, event_name, obj_name, tag, scale, down_scale, px=0, py=0):
        self.add(ButtonGen(gfx_type, gfx_name, event_name, obj_name, tag, self.optimal_scale * scale, down_scale ), name=obj_name)
        button = self.children_names[obj_name]
        if px == 0:
            button.x = self.optimal_width * self.button_positions[obj_name]["X"] + self.left_margin
        else:
            button.x = px
        if py == 0:
            button.y = self.optimal_height * self.button_positions[obj_name]["Y"] + self.bottom_margin
        else:
            button.y = py
