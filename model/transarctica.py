# -*- coding: utf-8 -*-
from model import Config
from cocos.director import director
import random

class Transarctica(object):
    """player object"""
    directions = {"N", "B", "E", "C", "S", "D", "W", "A"}

    def __init__(self):
        """initilaizer"""
        self.config = Config()
        self.direction = "W"
        self.is_in_reverse = False
        self.is_break_released = True
        self.speed = 0
        self.Speed_Regulator = 100
        self.Speed_Modifier = 1
        self.target_speed = 0
        self.train_layout = {}  
        self.cargo_manifest = {} 
        self.storage_cap = {}
        self.temp_modifiers = {}
        self.shovel_rate = {"Lignite": 0, "Anthracite": 0}
        self.refresh_counter = {"Lignite": 0, "Anthracite": 0}
        self.hpz = 160
        self.engine_temp = 0
        self.boiler_pressure = 0
        self.train_total_weight = 1265
        self.in_city = ""
        self.update_minitrain=False
        self.current_position = self.config.start_position#{"X": 1, "Y": 1}
        self.last_event_position = {"X": 1, "Y": 1}
        self.vis_range = self.config.base_vis_range
        self.opfor_id=-1
        self.proximity_alarm=0
        self.map = None


    def update_telemetry(self, time_change):
        if self.is_break_released:
            self.align_speed(time_change)
        if self.shovel_rate["Anthracite"]>0:
            self.refresh_counter["Anthracite"] += time_change
            if self.refresh_counter["Anthracite"] >= 6//self.shovel_rate["Anthracite"]:
                self.shoveling("Anthracite",self.config.anthracite_shovel_qty*(self.refresh_counter["Anthracite"]//(6//self.shovel_rate["Anthracite"])))
                if self.shovel_rate["Anthracite"]>0: 
                    self.refresh_counter["Anthracite"] %= (6//self.shovel_rate["Anthracite"])
        if self.shovel_rate["Lignite"]>0:
            self.refresh_counter["Lignite"] += time_change
            if self.refresh_counter["Lignite"] >= 6//self.shovel_rate["Lignite"]:
                self.shoveling("Lignite",self.config.anthracite_shovel_qty*(self.refresh_counter["Lignite"]//(6//self.shovel_rate["Lignite"])))
                if self.shovel_rate["Lignite"]>0: 
                    self.refresh_counter["Lignite"] %= (6//self.shovel_rate["Lignite"])

        self.engine_cooling(time_change)
        self.update_hpz(time_change)


    def align_speed(self,time_change):
        """
        Align current speed to target speed.
        Call it from the game's main loop until target_speed is reached.
        Does nothing if target speed and current speed are equal.
        """
        self.target_speed=self.config.maximum_speed * self.Speed_Regulator / 100 * min(1,self.hpz) * self.Speed_Modifier
        if self.target_speed > self.speed: #speeding up
            current_limit = min(self.config.maximum_speed * self.Speed_Modifier, self.target_speed)
            if current_limit - self.speed < (self.config.speeding_rate*time_change):
                current_speeding_rate = current_limit - self.speed
            else:
                current_speeding_rate = (self.config.speeding_rate*time_change)
        elif self.target_speed < self.speed: #slowing down
            current_limit = max(self.config.minimum_speed, self.target_speed)
            if current_limit - self.speed > self.config.breaking_rate:
                current_speeding_rate = current_limit - self.speed
            else:
                current_speeding_rate = self.config.breaking_rate
        else:
            current_speeding_rate = 0
        self.speed += current_speeding_rate


    def do_shovel(self,coal_type):
        self.shovel_rate[coal_type]=(self.shovel_rate[coal_type]+1)% 3
        if self.shovel_rate[coal_type]==0:
            self.refresh_counter[coal_type]=0


    def shoveling(self, type, qty):
        if (self.change_cargo_manifest("R", self.get_item_id_from_name(type), 0, qty))!="Y":
            qty=0
            self.shovel_rate[type]=0
            self.refresh_counter[type]=0
        if type=="Lignite":
            qty = qty / 3
        if self.boiler_pressure >= 110:
            self.boiler_pressure = self.boiler_pressure + qty*0
        elif self.boiler_pressure >= 108:
            self.boiler_pressure = self.boiler_pressure + qty*0.08
        elif self.boiler_pressure >= 104:
            self.boiler_pressure = self.boiler_pressure + qty*0.16
        elif self.boiler_pressure >= 98:
            self.boiler_pressure = self.boiler_pressure + qty*0.24
        elif self.boiler_pressure >= 90:
            self.boiler_pressure = self.boiler_pressure + qty*0.32
        elif self.boiler_pressure >= 80:
            self.boiler_pressure = self.boiler_pressure + qty*0.4
        elif self.boiler_pressure >= 68:
            self.boiler_pressure = self.boiler_pressure + qty*0.48
        elif self.boiler_pressure >= 54:
            self.boiler_pressure = self.boiler_pressure + qty*0.56
        elif self.boiler_pressure >= 38:
            self.boiler_pressure = self.boiler_pressure + qty*0.64
        elif self.boiler_pressure >= 20:
            self.boiler_pressure = self.boiler_pressure + qty*0.72
        elif self.boiler_pressure < 20:
            self.boiler_pressure = self.boiler_pressure + qty*0.8
        self.update_engine_temp()

    def engine_cooling(self,time_change):
        self.boiler_pressure = max(0,self.boiler_pressure - (self.config.boiler_cooldown_rate*time_change))
        self.update_engine_temp()

    def update_engine_temp(self):
        self.engine_temp = min(600,self.boiler_pressure * 35)


    def init_train(self):
        for storage_type in self.config.conf_storage_type:
            self.storage_cap[storage_type] = {} 
            self.storage_cap[storage_type]["max"]=0
            self.storage_cap[storage_type]["current"]=0
        for item in self.config.conf_items:
            self.cargo_manifest[item] = {} 
            self.cargo_manifest[item]["hold"]=0
            self.cargo_manifest[item]["value"]=0
            self.cargo_manifest[item]["loss"]=0
            self.cargo_manifest[item]["gain"]=0


    def init_assets(self):
        for wagon in self.config.start_train:
            for wagon_id in self.config.conf_wagons:
                if self.config.conf_wagons[wagon_id].wagon_name==wagon:
                    self.change_train_layout("A", wagon_id, 0, 1, -1)
        for item in self.config.start_items:
            for item_id in self.config.conf_items:
                if self.config.conf_items[item_id].item_name==item:
                    self.change_cargo_manifest("A", item_id, 0, self.config.start_items[item])
                    try:
                        self.cargo_manifest[item_id]["value"]=int(self.config.start_items_values[item])
                    except:
                        self.cargo_manifest[item_id]["value"]=int(self.config.conf_items[item_id].avg_price)

    def change_train_layout(self, action, wagon_id_1, price, qty, wagon_id_2):
        success=""
        if action=="A":
            res = self.change_cargo_manifest("R",self.get_item_id_from_name("Lignite"), 0, price)
            if res == "Y":
                self.train_layout[len(self.train_layout)]=wagon_id_1
                success="Y"
            else:
                success="Insufficient Lignite!"
        elif action=="R" :
            for wg in self.train_layout:
                if self.config.conf_wagons[self.train_layout[wg]].base_id==wagon_id_1:
                    last=wg
                    success="Y"
            if success=="Y":
                sell_wagon=self.config.conf_wagons[self.train_layout[last]]
                if sell_wagon.storage=="coal":
                    tender_revenue=price
                else:
                    tender_revenue=0
                if self.storage_cap[sell_wagon.storage]["max"]-int(sell_wagon.capacity)>=self.storage_cap[sell_wagon.storage]["current"]+tender_revenue:
                    res = self.change_cargo_manifest("A",self.get_item_id_from_name("Lignite"), 0, price)
                    if res == "Y":
                        del self.train_layout[last]
                    else:
                        success="Insufficient tender capacity!"
                else:
                    if tender_revenue>0:
                        success="Insufficient tender capacity!"
                    else:
                        success="Wagon in use!"
        elif action=="F":
            res = self.change_cargo_manifest("R",self.get_item_id_from_name("Lignite"), 0, price)
            if res == "Y":
                self.train_layout[wagon_id_1]=self.config.conf_wagons[self.train_layout[wagon_id_1]].base_id
                success="Y"
            else:
                success="Insufficient Lignite!"
        elif action=="D":
            base_id=self.config.conf_wagons[self.train_layout[wagon_id_1]].base_id
            new_damage=self.config.conf_wagons[self.train_layout[wagon_id_1]].damage+1
            if new_damage<=3:
                for wagon_id in self.config.conf_wagons:
                    if self.config.conf_wagons[wagon_id].base_id==base_id and self.config.conf_wagons[wagon_id].damage==new_damage:
                        self.train_layout[wagon_id_1]=wagon_id
            success="Y"
        elif action=="M" :
            if (self.change_cargo_manifest("R",self.get_item_id_from_name("Lignite"), 0, price))=="Y" and (wagon_id_1>=100 or wagon_id_2>=100):
                id_1=-1
                id_2=-1
                if (wagon_id_1>=100 and wagon_id_1%100<wagon_id_2) or (wagon_id_2>=100 and wagon_id_2%100>wagon_id_1):
                    id_1=wagon_id_1
                    id_2=wagon_id_2
                elif (wagon_id_1>=100 and wagon_id_1%100>wagon_id_2) or (wagon_id_2>=100 and wagon_id_2%100<wagon_id_1):
                    id_1=wagon_id_2
                    id_2=wagon_id_1
                if id_1>=100:
                    k=id_2
                    temp=self.train_layout[k]
                    while k > id_1%100:
                        self.train_layout[k]=self.train_layout[k-1]
                        k-=1
                    self.train_layout[id_1%100]=temp
                    success="Y"
                elif id_2>=100:
                    k=id_1
                    temp=self.train_layout[k]
                    while k < (id_2%100)-1:
                        self.train_layout[k]=self.train_layout[k+1]
                        k+=1
                    self.train_layout[(id_2%100)-1]=temp
                    success="Y"
            else:
                temp=self.train_layout[wagon_id_1]
                self.train_layout[wagon_id_1]=self.train_layout[wagon_id_2]
                self.train_layout[wagon_id_2]=temp
                success="Y"
        if success:             
            self.update_minitrain=True
            self.calculate_storage_cap()
            self.calculate_total_weight()
            self.calculate_vis_range()
        return success


    def change_cargo_manifest(self, action, item_id, price, qty):
        storage_type=self.config.conf_items[item_id].storage
        success=""
        if action=="A":
            if (self.storage_cap[storage_type]["max"]>=self.storage_cap[storage_type]["current"]+qty): 
                if (self.cargo_manifest[self.get_item_id_from_name("Lignite")]["hold"]-price>=0):
                    self.cargo_manifest[item_id]["value"]=self.cargo_manifest[item_id]["value"]*self.cargo_manifest[item_id]["hold"]+int(price)
                    self.cargo_manifest[item_id]["hold"]=self.cargo_manifest[item_id]["hold"]+qty
                    self.cargo_manifest[item_id]["value"]=self.cargo_manifest[item_id]["value"]/self.cargo_manifest[item_id]["hold"]
                    self.storage_cap[storage_type]["current"]=self.storage_cap[storage_type]["current"]+qty
                    if price != 0:
                        self.change_cargo_manifest("R", self.get_item_id_from_name("Lignite"), 0, price)
                    success="Y"
                else:
                    success="Not enough Lignite!"
            else:
                success="Insufficient storage capacity!"
        if action=="R":
            if (self.cargo_manifest[item_id]["hold"]-qty>=0):
                if (self.cargo_manifest[self.get_item_id_from_name("Lignite")]["hold"]+price<=self.storage_cap["coal"]["max"]):
                    self.cargo_manifest[item_id]["hold"]=self.cargo_manifest[item_id]["hold"]-qty
                    self.storage_cap[storage_type]["current"]=self.storage_cap[storage_type]["current"]-qty
                    if price != 0:
                        self.change_cargo_manifest("A", self.get_item_id_from_name("Lignite"), 0, price)
                    success="Y"
                    if self.cargo_manifest[item_id]["hold"]==0:
                        self.cargo_manifest[item_id]["value"]=0    
                else:
                    success="Insufficient tender capacity!"
            else:
                success="Not enough items to sell!"
        if success=="Y":
            self.calculate_total_weight()
        return success

    def get_item_id_from_name(self, item_name):
        for item_id in self.config.conf_items:
            if self.config.conf_items[item_id].item_name==item_name:
                return item_id

    def calculate_total_weight(self):
        self.train_total_weight=self.calculate_wagon_weight()+self.calculate_cargo_weight()
        
    def calculate_wagon_weight(self):
        total_weight=0
        for wg in self.train_layout:
            total_weight += int(self.config.conf_wagons[self.train_layout[wg]].net_weight)
        return total_weight

    def calculate_cargo_weight(self):
        total_weight=0
        for storage_type in self.config.conf_storage_type:
            if storage_type in ["goods","plants","perishable", "liquids", "mammoths"]:
                total_weight += self.storage_cap[storage_type]["current"]
            if storage_type in ["soldiers","slaves"]:
                total_weight += self.storage_cap[storage_type]["current"]//10
            if storage_type in ["coal"]:
                total_weight += self.storage_cap[storage_type]["current"]//100
        return total_weight

    def calculate_storage_cap(self):
        for storage_type in self.config.conf_storage_type:
            self.storage_cap[storage_type]["max"]=0
        for wg in self.train_layout:
            self.storage_cap[self.config.conf_wagons[self.train_layout[wg]].storage]["max"]=self.storage_cap[self.config.conf_wagons[self.train_layout[wg]].storage]["max"]+int(self.config.conf_wagons[self.train_layout[wg]].capacity)
        
    def calculate_vis_range(self):
        self.vis_range = self.config.base_vis_range + self.storage_cap["telescopes"]["max"]
        


    def count_wagon_with_id(self, wagon_id):
        count=0
        for wg in self.train_layout:
            if self.config.conf_wagons[self.train_layout[wg]].base_id==wagon_id:
                count += 1
        return count

    def update_hpz(self,time_change):
        if self.boiler_pressure > 4:
            self.hpz = min(160, self.hpz+time_change)
        else:
            self.hpz = max(0,self.hpz-(((self.speed*self.speed)/3000) * (self.train_total_weight/1515)/78)*time_change)

    def calculate_force_value(self, engagement):
        force=0
        if engagement=="long_range":
            force+=self.storage_cap["shells"]["max"]//20
            force+=self.storage_cap["belts"]["max"]//10
            for item_id in self.cargo_manifest:
                if self.config.conf_items[item_id].storage in ["soldiers"]:
                    force+= int(self.cargo_manifest[item_id]["hold"])*int(self.config.conf_items[item_id].LRCV)
        elif engagement=="short_range":
            force+=self.storage_cap["shells"]["max"]//5
            force+=self.storage_cap["belts"]["max"]//10
            for item_id in self.cargo_manifest:
                if self.config.conf_items[item_id].storage in ["soldiers","mammoths"]:
                    force+= int(self.cargo_manifest[item_id]["hold"])*int(self.config.conf_items[item_id].CQCV)
        elif engagement=="build":
            force+=self.storage_cap["crane"]["max"]*50
            for item_id in self.cargo_manifest:
                if self.config.conf_items[item_id].storage in ["soldiers","mammoths","slaves"]:
                    force+= int(self.cargo_manifest[item_id]["hold"])*int(self.config.conf_items[item_id].BuildV)
        elif engagement=="hunt":
            force+=self.storage_cap["belts"]["max"]//10
            for item_id in self.cargo_manifest:
                if self.config.conf_items[item_id].storage in ["soldiers","mammoths","slaves"]:
                    force+= int(self.cargo_manifest[item_id]["hold"])*int(self.config.conf_items[item_id].HuntV)
        return force

    def calculate_loot_loss(self, type, loot_perc):
        for item_id in self.cargo_manifest:
            self.cargo_manifest[item_id]["loss"]=0
        if type=="molemen":
            for item_id in self.cargo_manifest:
                if self.cargo_manifest[item_id]["hold"]>0:
                    for i in range(1, self.cargo_manifest[item_id]["hold"], 1):
                        if random.randint(1, 100)<loot_perc:
                            self.change_cargo_manifest("R", item_id, 0, 1)
                            self.cargo_manifest[item_id]["loss"]+=1
            return ""
        if type=="mammoth_herd":
            for item_id in self.cargo_manifest:
                if self.cargo_manifest[item_id]["hold"]>0 and (self.config.conf_items[item_id].storage in ["soldiers", "mammoths", "slaves"] or self.config.conf_items[item_id].item_name in ["Meat","Vegetables","Grain"]) :
                    for i in range(1, self.cargo_manifest[item_id]["hold"], 1):
                        if random.randint(1, 100)<loot_perc:
                            self.change_cargo_manifest("R", item_id, 0, 1)
                            self.cargo_manifest[item_id]["loss"]+=1
            return ""
        if type=="bridge_monster":
            message="No damage."
            for item_id in self.cargo_manifest:
                if self.cargo_manifest[item_id]["hold"]>0 and (self.config.conf_items[item_id].storage in ["soldiers", "mammoths", "slaves"] or self.config.conf_items[item_id].item_name in ["Meat"]) :
                    for i in range(1, self.cargo_manifest[item_id]["hold"], 1):
                        if random.randint(1, 100)<loot_perc:
                            self.change_cargo_manifest("R", item_id, 0, 1)
                            self.cargo_manifest[item_id]["loss"]+=1
            for wg in self.train_layout:
                if self.config.conf_wagons[self.train_layout[wg]].damage==0 and random.randint(1, 100)<loot_perc*2:
                   self.change_train_layout("D", wg, 0, 1, -1)
                   if message=="No damage." :
                       message="The train suffered some damage."
                if self.config.conf_wagons[self.train_layout[wg]].damage==1 and random.randint(1, 100)<loot_perc:
                   self.change_train_layout("D", wg, 0, 1, -1)
                   message="The train suffered heavy damage."
            return message
        if type=="train_combat":
            message="No damage."
            for item_id in self.cargo_manifest:
                if self.cargo_manifest[item_id]["hold"]>0 and self.config.conf_items[item_id].storage in ["soldiers", "mammoths", "slaves"]  :
                    for i in range(1, self.cargo_manifest[item_id]["hold"], 1):
                        if random.randint(1, 100)<loot_perc:
                            self.change_cargo_manifest("R", item_id, 0, 1)
                            self.cargo_manifest[item_id]["loss"]+=1
            for wg in self.train_layout:
                if self.config.conf_wagons[self.train_layout[wg]].damage==0 and random.randint(1, 100)<loot_perc*2:
                   self.change_train_layout("D", wg, 0, 1, -1)
                   if message=="No damage." :
                       message="The train suffered some damage."
                if self.config.conf_wagons[self.train_layout[wg]].damage==1 and random.randint(1, 100)<loot_perc:
                   self.change_train_layout("D", wg, 0, 1, -1)
                   message="The train suffered heavy damage."
            return message

    def calculate_loot_gain(self, type, ownfor, opfor):
        for item_id in self.cargo_manifest:
            self.cargo_manifest[item_id]["gain"]=0
        act_value=0
        if type=="mammoth_herd":
            gain_value=random.randint(min(ownfor, opfor), opfor)*min(1.5,max(1,ownfor/opfor))  
            while act_value<gain_value:
                for item_id in self.cargo_manifest:
                    if self.config.conf_items[item_id].storage in ["mammoths"]  :
                        if (random.randint(1,100)>=int(self.config.conf_items[item_id].avg_price)) and (act_value<gain_value)  :
                            if self.change_cargo_manifest("A", item_id, 0, 1)=="Y" :
                                self.cargo_manifest[item_id]["gain"]+=1
                                act_value+=int(self.config.conf_items[item_id].avg_price)
                            else:
                                act_value=gain_value
            return ""
        if type=="train_combat":
            gain_value=max(0,min(1000,(((100*ownfor)//(opfor*1.2))-100)*random.randint(4,8)))
            while act_value<gain_value:
                for item_id in self.cargo_manifest:
                    if self.config.conf_items[item_id].storage in ["coal"]  :
                        if act_value<gain_value :
                            for j in range(random.randint(50,200)) :
                                if self.change_cargo_manifest("A", item_id, 0, 1)=="Y" :
                                    self.cargo_manifest[item_id]["gain"]+=1
                                act_value+=int(self.config.conf_items[item_id].avg_price)
                for item_id in self.cargo_manifest:
                    if self.config.conf_items[item_id].storage in ["slaves", "goods"]  :
                        if (random.randint(1,40)>=int(self.config.conf_items[item_id].avg_price)) and (act_value<gain_value)  :
                            for j in range(random.randint(1,10)):
                                if self.change_cargo_manifest("A", item_id, 0, 1)=="Y" :
                                    self.cargo_manifest[item_id]["gain"]+=1
                                act_value+=int(self.config.conf_items[item_id].avg_price)
            gain_list=""
            for item_id in self.cargo_manifest:
                    if self.cargo_manifest[item_id]["gain"]>0  :
                        gain_list+=self.config.conf_items[item_id].screen_name+": "+str(self.cargo_manifest[item_id]["gain"])+", "
            return gain_list

    def game_loaded(self,game_object):
        self.direction = game_object["direction"]
        self.is_in_reverse = game_object["is_in_reverse"]
        self.is_break_released = game_object["is_break_released"]
        self.speed = game_object["speed"]
        self.Speed_Regulator = game_object["Speed_Regulator"]
        self.target_speed = game_object["target_speed"]
        self.hpz = game_object["hpz"]
        self.engine_temp = game_object["engine_temp"]
        self.boiler_pressure = game_object["boiler_pressure"]
        self.current_position = game_object["current_position"]
        self.config.start_train.clear()
        self.config.start_train=game_object["start_train"]

                
    def current_timestamp(self):
        return director.core.timestamp