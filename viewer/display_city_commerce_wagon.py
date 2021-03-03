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
import random

class DisplayCityCommerceWagon(Layer):
    display_pos_size = {"display_city_commerce": {"X": 0, "Y": 0.175, "W":1, "H":0.75}}
    button_positions = {"label_cityname": {"X": 0.5, "Y": 0.97},
                        "button_city_table": {"X": 0.0, "Y": 0.984},
                        "button_exit": {"X": 0.88, "Y": -0.16},
                        "button_switch": {"X": 0.77, "Y": -0.16},
                        "label_stores_1": {"X": 0.055, "Y": -0.051, "fsize": 16},
                        "label_stores_2": {"X": 0.055, "Y": -0.081, "fsize": 16},
                        "label_stores_3": {"X": 0.055, "Y": -0.111, "fsize": 16},
                        "sprite_wagon_selected": {"X": 0.055, "Y": 0.235},
                        "label_wagon_name": {"X": 0.055, "Y": -0.051, "fsize": 16},
                        "label_wagon_stats": {"X": 0.055, "Y": -0.081, "fsize": 16},
                        "label_lignite_you_have": {"X": 0.055, "Y": -0.141, "fsize": 16},
                        "label_line_5": {"X": 0.055, "Y": -0.171, "fsize": 16}}

    max_wagon_count_on_market = {"commerce": 10, "hub": 14, "barracks": 3, "mammoth": 2, "wagon": 8, "slave": 2}

    def __init__(self, market):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self.wagons_for_trade = {}
        self.wagons_for_dump = {}
        self.message=""
        self.trade_display = True
        self.market=market
        self.generate_wagons_for_trade()
        self.generate_wagons_for_dump()
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

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["city_"+self.market])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_city_commerce"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_city_commerce"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_city_commerce"]["Y"]
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
        label_stores_1 = self._load_label_gen("label_stores_1")
        self.add(label_stores_1, name="label_stores_1")
        self.get("label_stores_1").element.text=" "
        label_stores_2 = self._load_label_gen("label_stores_2")
        self.add(label_stores_2, name="label_stores_2")
        self.get("label_stores_2").element.text=" "
        label_stores_3 = self._load_label_gen("label_stores_3")
        self.add(label_stores_3, name="label_stores_3")
        self.get("label_stores_3").element.text=" "
        label_lignite_you_have = self._load_label_gen("label_lignite_you_have")
        self.add(label_lignite_you_have, name="label_lignite_you_have")
        self.get("label_lignite_you_have").element.text=" "

        for j in range(50):
            self.button_positions["sprite_trade_bracket"+str(j)] = {"X": 0.05+(0.225*(j%4)),"Y": 1.03-(0.183*(j//4))}
            self.button_positions["trade_bracket"+str(j)] = {"X": 0.05+(0.225*(j%4)),"Y": 0.804-(0.183*(j//4))}
            self.button_positions["button_buy"+str(j)] = {"X": 0.225+(0.225*(j%4)),"Y": 0.896-(0.183*(j//4))}
            self.button_positions["button_sell"+str(j)] = {"X": 0.225+(0.225*(j%4)),"Y": 0.846-(0.183*(j//4))}
        self._load_trade_boxes()

    def switch_trade_dump(self):
        self.trade_display = not(self.trade_display)
        self.generate_wagons_for_dump()
        self._load_trade_boxes()


    def _load_trade_boxes(self):
        self.remove_trade_boxes()
        if self.trade_display:
            self._load_button_gen("button", "drop", events.emit_commerce_switch_trade_dump, "button_switch", 0, 1, 0.95)
            for wagon in self.wagons_for_trade:
                self._load_button_gen("wagon", self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].display_image+"_t", events.emit_wagon_select, "trade_bracket"+str(wagon), wagon, 1, 0.99 )
                label_wagon_name = Label(self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].wagon_name + " ("+self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].storage+")", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(wagon)]["X"]+0.112), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(wagon)]["Y"]+0.152)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=16*self.optimal_scale, anchor_x="center", anchor_y="center")
                self.add(label_wagon_name, name="trade_bracket_wagon_name"+str(wagon))
                label_wagon_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(wagon)]["X"]+0.112), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(wagon)]["Y"]+0.026)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="center", anchor_y="center")
                self.add(label_wagon_name, name="trade_bracket_wagon_hold"+str(wagon))
                self._load_button_gen("button", "plus", events.emit_item_buy, "button_buy"+str(wagon), wagon, 0.72, 0.95 )
                self._load_button_gen("button", "minus", events.emit_item_sell, "button_sell"+str(wagon), wagon, 0.72, 0.95 )
        else:
            self._load_button_gen("button", "trade", events.emit_commerce_switch_trade_dump, "button_switch", 0, 1, 0.95)
            for wagon in self.wagons_for_dump:
                trade_bracket = Sprite(self.gallery.content["wagon"][self.config.conf_wagons[self.wagons_for_dump[wagon]["wagon_id"]].display_image+"_t"])
                trade_bracket.image_anchor = 0, 0
                trade_bracket.scale = self.optimal_scale
                trade_bracket.x = self.optimal_width * self.button_positions["sprite_trade_bracket"+str(wagon)]["X"]
                trade_bracket.y = self.optimal_height * self.button_positions["sprite_trade_bracket"+str(wagon)]["Y"]
                self.add(trade_bracket, name="trade_bracket"+str(wagon))
                label_wagon_name = Label(self.config.conf_wagons[self.wagons_for_dump[wagon]["wagon_id"]].wagon_name + " ("+self.config.conf_wagons[self.wagons_for_dump[wagon]["wagon_id"]].storage+")", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(wagon)]["X"]+0.112), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(wagon)]["Y"]+0.152)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=16*self.optimal_scale, anchor_x="center", anchor_y="center")
                self.add(label_wagon_name, name="trade_bracket_wagon_name"+str(wagon))
                label_wagon_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(wagon)]["X"]+0.112), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(wagon)]["Y"]+0.026)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="center", anchor_y="center")
                self.add(label_wagon_name, name="trade_bracket_wagon_hold"+str(wagon))
                self._load_button_gen("button", "minus", events.emit_item_sell, "button_sell"+str(wagon), wagon, 0.72, 0.95 )
        self.update_desc()

    def remove_trade_boxes(self):
        try:
            self.remove("button_switch")
        except:
            A=1
        try:
            self.remove("sprite_wagon_selected")
        except:
            A=1

        for j in range(50):
            try:
                self.remove("trade_bracket"+str(j))
                self.remove("trade_bracket_wagon_name"+str(j))
                self.remove("trade_bracket_wagon_hold"+str(j))
                self.remove("button_sell"+str(j))
            except:
                A=1
            try:
                self.remove("button_buy"+str(j))
            except:
                A=1
        self.get("label_stores_1").element.text=" "
        self.get("label_stores_2").element.text=" "
    
    def generate_wagons_for_dump(self):
        self.wagons_for_dump.clear()
        for wagon_id in range(self.config.base_wagon_range):
            wagon_count = self.transarctica.count_wagon_with_id(wagon_id)
            if wagon_count>0 and self.config.conf_wagons[wagon_id].rarity!="0":
                i=len(self.wagons_for_dump)
                self.wagons_for_dump[i]={}
                self.wagons_for_dump[i]["wagon_id"]=wagon_id
                self.wagons_for_dump[i]["price"] = 0
                self.wagons_for_dump[i]["buy_units"]=99999                    
                self.wagons_for_dump[i]["sell_units"]=0

    def generate_wagons_for_trade(self):
        k=0
        while k < self.max_wagon_count_on_market[self.market]:
            wagon_id=random.randint(0,self.config.base_wagon_range-1)
            try:
                rarity_val = int(self.config.conf_wagons[wagon_id].rarity)
            except ValueError:
                if self.transarctica.in_city==self.config.conf_wagons[wagon_id].rarity:
                    rarity_val = 1
                else:
                    rarity_val = 0
            if rarity_val > 0 and random.randint(1,rarity_val)==1:
                in_list=False
                for wagon in self.wagons_for_trade:
                    if self.wagons_for_trade[wagon]["wagon_id"]==wagon_id:
                        self.wagons_for_trade[wagon]["sell_units"]+=random.randint(1,2)
                        in_list=True
                if not(in_list):
                    i=len(self.wagons_for_trade)
                    self.wagons_for_trade[i]={}
                    self.wagons_for_trade[i]["wagon_id"]=wagon_id
                    self.wagons_for_trade[i]["price"]=random.randint(int(self.config.conf_wagons[wagon_id].avg_price)//2,int(self.config.conf_wagons[wagon_id].avg_price))+int(self.config.conf_wagons[wagon_id].avg_price)//4
                    self.wagons_for_trade[i]["sell_units"]=random.randint(1,2)
                    self.wagons_for_trade[i]["buy_units"]=random.randint(0,3+rarity_val)
                    k=k+random.randint(1,2)

    def do_transaction(self, Action, tag):
        if Action=="buy":
            if (self.wagons_for_trade[tag]["sell_units"] > 0): 
                res = (self.transarctica.change_train_layout("A", self.wagons_for_trade[tag]["wagon_id"], self.wagons_for_trade[tag]["price"], 1,-1))
                if res=="Y":
                    self.message=""
                    self.wagons_for_trade[tag]["sell_units"]=self.wagons_for_trade[tag]["sell_units"]-1
                else:
                    self.message=res+" "   
        if Action=="sell":
            if self.trade_display:
                if self.wagons_for_trade[tag]["buy_units"] > 0:
                    res = self.transarctica.change_train_layout("R", self.wagons_for_trade[tag]["wagon_id"], self.wagons_for_trade[tag]["price"], 1,-1)
                    if res=="Y":
                        self.message=""
                        self.wagons_for_trade[tag]["buy_units"]=self.wagons_for_trade[tag]["buy_units"]-1
                    else:
                        self.message=res+" "   

            else:
                res = self.transarctica.change_train_layout("R", self.wagons_for_dump[tag]["wagon_id"], 0, 1, -1)
                if res=="Y":
                    self.message=""
                else:
                    self.message=res +" "
        self.update_desc()

    def display_wagon_info(self, wagon):
        try:
            self.remove("sprite_wagon_selected")
        except:
            A=1
        wagon_selected = Sprite(self.gallery.content["wagon"][self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].display_image+"_c"])
        wagon_selected.image_anchor = 0, 0
        wagon_selected.scale = self.optimal_scale*1.66
        wagon_selected.x = self.optimal_width * self.button_positions["sprite_wagon_selected"]["X"]
        wagon_selected.y = self.optimal_height * self.button_positions["sprite_wagon_selected"]["Y"]
        self.add(wagon_selected, name="sprite_wagon_selected")
        self.get("label_stores_1").element.text=self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].screen_name
        self.get("label_stores_2").element.text="Net weight: "+self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].net_weight+", Capacity: "+self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].capacity+str(self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].units)+self.config.conf_wagons[self.wagons_for_trade[wagon]["wagon_id"]].storage
        self.update_desc()

    def update_desc(self):
        if self.trade_display:
            for wagon in self.wagons_for_trade:
                self.get("trade_bracket_wagon_hold"+str(wagon)).element.text="Supply: "+str(self.wagons_for_trade[wagon]["sell_units"])+ ", Demand: "+str(self.wagons_for_trade[wagon]["buy_units"])+ ", Price:"+str(self.wagons_for_trade[wagon]["price"]) 
                self.get("label_lignite_you_have").element.text=self.message+"You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"
        else:
            for wagon in self.wagons_for_dump:
                self.get("trade_bracket_wagon_hold"+str(wagon)).element.text="Have: "+str(self.transarctica.count_wagon_with_id(self.wagons_for_dump[wagon]["wagon_id"]))
                self.get("label_lignite_you_have").element.text=self.message+"You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"

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
