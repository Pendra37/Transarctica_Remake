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

class DisplayCityCommerce(Layer):
    display_pos_size = {"display_city_commerce": {"X": 0, "Y": 0.175, "W":1, "H":0.75}}
    button_positions = {"overlay_commerce_type": {"X": 0.0, "Y": 0.0},
                        "label_cityname": {"X": 0.5, "Y": 0.97},
                        "button_city_table": {"X": 0.0, "Y": 0.984},
                        "button_exit": {"X": 0.88, "Y": -0.16},
                        "button_switch": {"X": 0.77, "Y": -0.16},
                        "label_stores_1": {"X": 0.055, "Y": -0.051, "fsize": 16},
                        "label_stores_2": {"X": 0.055, "Y": -0.081, "fsize": 16},
                        "label_stores_3": {"X": 0.055, "Y": -0.111, "fsize": 16},
                        "label_lignite_you_have": {"X": 0.055, "Y": -0.141, "fsize": 16},
                        "label_line_5": {"X": 0.055, "Y": -0.171, "fsize": 16}}

    max_item_count_on_market = {"commerce": 12, "hub": 17, "barracks": 3, "mammoth": 2, "wagon": 6, "slave": 2}
    storage_groups = {"commerce": {"goods","perishable","plants","liquids"},
                      "hub": {"goods","perishable","plants","liquids"},
                      "barracks": {"soldiers"},
                      "mammoth": {"mammoths"},
                      "slave": {"slaves"},
                      "wagon": {"goods"}}

    def __init__(self, supply, market):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self.items_for_trade = {}
        self.items_for_dump = {}
        self.message=""
        self.trade_display = True
        #if (supply=="hub") and (market=="commerce"):
        #    self.market=supply
        #else:
        self.market=market
        self.supply=supply
        self.generate_items_for_trade(supply)
        self.generate_items_for_dump()
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
        if self.market=="commerce":
            overlay = Sprite(self.gallery.content["display"]["city_commerce_"+self.supply])
            overlay.image_anchor = 0, 0
            overlay.x=self.left_margin
            overlay.y=self.bottom_margin
            overlay.scale = self.optimal_scale
            self.add(overlay)


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
            self.button_positions["button_buy"+str(j)] = {"X": 0.225+(0.225*(j%4)),"Y": 0.896-(0.183*(j//4))}
            self.button_positions["button_sell"+str(j)] = {"X": 0.225+(0.225*(j%4)),"Y": 0.846-(0.183*(j//4))}
        self._load_trade_boxes()

    def switch_trade_dump(self):
        self.trade_display = not(self.trade_display)
        self.generate_items_for_dump()
        self._load_trade_boxes()


    def _load_trade_boxes(self):
        self.remove_trade_boxes()
        if self.trade_display:
            self._load_button_gen("button", "drop", events.emit_commerce_switch_trade_dump, "button_switch", 0, 1, 0.95)
            for item in self.items_for_trade:
                trade_bracket = Sprite(self.gallery.content["item"][self.config.conf_items[self.items_for_trade[item]["item_id"]].display_image+"_t"])
                trade_bracket.image_anchor = 0, 0
                trade_bracket.scale = self.optimal_scale
                trade_bracket.x = self.optimal_width * self.button_positions["sprite_trade_bracket"+str(item)]["X"]
                trade_bracket.y = self.optimal_height * self.button_positions["sprite_trade_bracket"+str(item)]["Y"]
                self.add(trade_bracket, name="trade_bracket"+str(item))
                label_item_name = Label(self.config.conf_items[self.items_for_trade[item]["item_id"]].item_name, (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.138), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.152)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=16*self.optimal_scale, anchor_x="center", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_name"+str(item))
                label_item_name = Label(self.config.conf_items[self.items_for_trade[item]["item_id"]].storage, (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.130)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_storage"+str(item))
                label_item_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.104)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_supply"+str(item))
                label_item_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.078)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_demand"+str(item))
                label_item_name = Label("Price: "+str(self.items_for_trade[item]["price"]), (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.052)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_price"+str(item))
                label_item_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.026)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_hold"+str(item))
                #if (self.items_for_trade[item]["sell_units"] > 0):
                self._load_button_gen("button", "plus", events.emit_item_buy, "button_buy"+str(item), item, 0.72, 0.95 )
                #if (self.items_for_trade[item]["buy_units"] > 0):
                self._load_button_gen("button", "minus", events.emit_item_sell, "button_sell"+str(item), item, 0.72, 0.95 )
        else:
            self._load_button_gen("button", "trade", events.emit_commerce_switch_trade_dump, "button_switch", 0, 1, 0.95)
            for item in self.items_for_dump:
                trade_bracket = Sprite(self.gallery.content["item"][self.config.conf_items[self.items_for_dump[item]["item_id"]].display_image+"_t"])
                trade_bracket.image_anchor = 0, 0
                trade_bracket.scale = self.optimal_scale
                trade_bracket.x = self.optimal_width * self.button_positions["sprite_trade_bracket"+str(item)]["X"]
                trade_bracket.y = self.optimal_height * self.button_positions["sprite_trade_bracket"+str(item)]["Y"]
                self.add(trade_bracket, name="trade_bracket"+str(item))
                label_item_name = Label(self.config.conf_items[self.items_for_dump[item]["item_id"]].item_name, (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.138), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.152)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=16*self.optimal_scale, anchor_x="center", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_name"+str(item))
                label_item_name = Label(self.config.conf_items[self.items_for_dump[item]["item_id"]].storage, (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.130)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_storage"+str(item))
                label_item_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.104)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="button_buy"+str(item)) #just to have an object with the name to remove
                self.add(label_item_name, name="trade_bracket_item_hold"+str(item))
                label_item_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.078)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_demand"+str(item))
                label_item_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.052)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_price"+str(item))
                label_item_name = Label(" ", (self.optimal_width * (self.button_positions["sprite_trade_bracket"+str(item)]["X"]+0.088), self.optimal_height*(self.button_positions["sprite_trade_bracket"+str(item)]["Y"]+0.026)), color=(0,0,0,255), font_name="Arial", bold=True, font_size=14*self.optimal_scale, anchor_x="left", anchor_y="center")
                self.add(label_item_name, name="trade_bracket_item_supply"+str(item))
                self._load_button_gen("button", "minus", events.emit_item_sell, "button_sell"+str(item), item, 0.72, 0.95 )
        self.update_desc()

    def remove_trade_boxes(self):
        try:
            self.remove("button_switch")
        except:
            A=1
        for j in range(50):
            try:
                self.remove("trade_bracket"+str(j))
                self.remove("trade_bracket_item_name"+str(j))
                self.remove("trade_bracket_item_storage"+str(j))
                self.remove("trade_bracket_item_supply"+str(j))
                self.remove("trade_bracket_item_demand"+str(j))
                self.remove("trade_bracket_item_price"+str(j))
                self.remove("trade_bracket_item_hold"+str(j))
                self.remove("button_sell"+str(j))
                self.remove("button_buy"+str(j))
            except:
                A=1

            
    def generate_items_for_dump(self):
        self.items_for_dump.clear()
        for item_id in self.transarctica.cargo_manifest:
            if (self.transarctica.cargo_manifest[item_id]["hold"]>0) and (self.market==self.config.conf_items[item_id].market):
                i=len(self.items_for_dump)
                self.items_for_dump[i]={}
                self.items_for_dump[i]["item_id"]=item_id
                self.items_for_dump[i]["price"] = 0
                self.items_for_dump[i]["buy_units"]=99999                    
                self.items_for_dump[i]["sell_units"]=0


    def generate_items_for_trade(self, supply):
        k=0
        if (supply != 'hub') and (self.market=="commerce"):
            while k < self.max_item_count_on_market[self.market]:
                item_id=random.randint(0,len(self.config.conf_items)-1)
                if self.config.conf_items[item_id].supply == supply:
                    in_list=False
                    for item in self.items_for_trade:
                        if self.items_for_trade[item]["item_id"]==item_id:
                            in_list=True
                    if not(in_list):
                        i=len(self.items_for_trade)
                        self.items_for_trade[i]={}
                        self.items_for_trade[i]["item_id"]=item_id
                        self.items_for_trade[i]["price"] = int(self.config.conf_items[item_id].avg_price) - random.randint(0,int(self.config.conf_items[item_id].avg_price)//2)
                        self.items_for_trade[i]["buy_units"]=0
                        self.items_for_trade[i]["sell_units"]=random.randint(min(max((40//int(self.items_for_trade[i]["price"])),1),9),10)*random.randint(1,(90//int(self.items_for_trade[i]["price"]))+1)
                        k=k+random.randint(1,2)
                else:
                    if (self.market==self.config.conf_items[item_id].market) and (random.randint(1,5)<=self.config.conf_city_sup_dem_matrix[supply][self.config.conf_items[item_id].supply]["need"]):
                        in_list=False
                        for item in self.items_for_trade:
                            if self.items_for_trade[item]["item_id"]==item_id:
                                in_list=True
                        if not(in_list):
                            i=len(self.items_for_trade)
                            self.items_for_trade[i]={}
                            self.items_for_trade[i]["item_id"]=item_id
                            self.items_for_trade[i]["price"]=int(self.config.conf_items[item_id].avg_price) + random.randint(1,(int(self.config.conf_items[item_id].avg_price)*int(self.config.conf_city_sup_dem_matrix[supply][self.config.conf_items[item_id].supply]["price_mod"]))//5+1)
                            self.items_for_trade[i]["buy_units"]=random.randint(max((40//int(self.items_for_trade[i]["price"])),1),10)*random.randint(1,(90//int(self.items_for_trade[i]["price"]))+1)
                            self.items_for_trade[i]["sell_units"]=0
                            k=k+random.randint(1,2)
        else:
            if (supply=="hub") and (self.market=="commerce"):
                item_count=self.max_item_count_on_market[supply]
            else:
                item_count=self.max_item_count_on_market[self.market]
            while k < item_count:
                item_id=random.randint(0,len(self.config.conf_items)-1)
                if (self.market==self.config.conf_items[item_id].market):
                    in_list=False
                    for item in self.items_for_trade:
                        if self.items_for_trade[item]["item_id"]==item_id:
                            in_list=True
                    if not(in_list):
                        i=len(self.items_for_trade)
                        self.items_for_trade[i]={}
                        self.items_for_trade[i]["item_id"]=item_id
                        self.items_for_trade[i]["price"]=(int(self.config.conf_items[item_id].avg_price) * random.randint(80,120))//100
                        self.items_for_trade[i]["buy_units"]=random.randint(1,10)*random.randint(1,(200//int(self.items_for_trade[i]["price"]))+1)
                        self.items_for_trade[i]["sell_units"]=random.randint(1,10)*random.randint(1,(200//int(self.items_for_trade[i]["price"]))+1)
                        k=k+random.randint(1,2)

    def do_transaction(self, Action, tag):
        if Action=="buy":
            if (self.items_for_trade[tag]["sell_units"] > 0): 
                res = (self.transarctica.change_cargo_manifest("A", self.items_for_trade[tag]["item_id"], self.items_for_trade[tag]["price"], 1))
                if res=="Y":
                    self.message=""
                    self.items_for_trade[tag]["sell_units"]=self.items_for_trade[tag]["sell_units"]-1
                else:
                    self.message=res+" "   
        if Action=="sell":
            if self.trade_display:
                if self.items_for_trade[tag]["buy_units"] > 0:
                    res = self.transarctica.change_cargo_manifest("R", self.items_for_trade[tag]["item_id"], self.items_for_trade[tag]["price"], 1)
                    if res=="Y":
                        self.message=""
                        self.items_for_trade[tag]["buy_units"]=self.items_for_trade[tag]["buy_units"]-1
                    else:
                        self.message=res+" "  
            else:
                res = self.transarctica.change_cargo_manifest("R", self.items_for_dump[tag]["item_id"], 0, 1)
                if res=="Y":
                    self.message=""
                else:
                    self.message=res+" "  
        self.update_desc()
 
    def update_desc(self):
        if self.trade_display:
            for item in self.items_for_trade:
                if (self.items_for_trade[item]["sell_units"] > 0):
                    self.get("trade_bracket_item_supply"+str(item)).element.text="Supply: "+str(self.items_for_trade[item]["sell_units"])
                else:
                    self.get("trade_bracket_item_supply"+str(item)).element.text=" "
                if (self.items_for_trade[item]["buy_units"] > 0):                
                    self.get("trade_bracket_item_demand"+str(item)).element.text="Demand: "+str(self.items_for_trade[item]["buy_units"])
                else:
                    self.get("trade_bracket_item_demand"+str(item)).element.text=" "
                self.get("trade_bracket_item_hold"+str(item)).element.text="Hold: "+str(self.transarctica.cargo_manifest[self.items_for_trade[item]["item_id"]]["hold"])+" Avg Price: "+str(round(self.transarctica.cargo_manifest[self.items_for_trade[item]["item_id"]]["value"],1))
                self.get("label_stores_1").element.text=""            
                for storage_type in self.transarctica.storage_cap:
                    if (str(self.transarctica.storage_cap[storage_type]["max"])!="0") and (storage_type in self.storage_groups[self.market]):
                        self.get("label_stores_1").element.text=self.get("label_stores_1").element.text+storage_type+": "+str(self.transarctica.storage_cap[storage_type]["current"])+"/"+str(self.transarctica.storage_cap[storage_type]["max"])+", "
                self.get("label_lignite_you_have").element.text=self.message+"You have "+str(self.transarctica.cargo_manifest[self.transarctica.get_item_id_from_name("Lignite")]["hold"]) + " baks lignite"
        else:
            for item in self.items_for_dump:
                self.get("trade_bracket_item_hold"+str(item)).element.text="Hold: "+str(self.transarctica.cargo_manifest[self.items_for_dump[item]["item_id"]]["hold"])+" Avg Price: "+str(round(self.transarctica.cargo_manifest[self.items_for_dump[item]["item_id"]]["value"],1))
                self.get("label_stores_1").element.text=""            
                for storage_type in self.transarctica.storage_cap:
                    if (str(self.transarctica.storage_cap[storage_type]["max"])!="0") and (storage_type in self.storage_groups[self.market]):
                        self.get("label_stores_1").element.text=self.get("label_stores_1").element.text+storage_type+": "+str(self.transarctica.storage_cap[storage_type]["current"])+"/"+str(self.transarctica.storage_cap[storage_type]["max"])+", "
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
