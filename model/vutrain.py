# -*- coding: utf-8 -*-
from model import Config
from cocos.director import director
import random

class VUTrain(object):
    """Viking Union Trains"""
    directions = {"N", "B", "E", "C", "S", "D", "W", "A"}

    def __init__(self):
        """initilaizer"""
        self.config = Config()
        self.direction = "E"
        self.is_in_reverse = False
        self.is_break_released = True
        self.speed = 0
        self.Speed_Regulator = random.randint(50, 90)
        self.Speed_Modifier = 1
        self.target_speed = 0
        self.train_layout = {}  
        self.cargo_manifest = {} 
        self.storage_cap = {}
        self.hpz = 160
        self.in_city = ""
        self.current_position = {"X": 15, "Y": 9}
        self.force_rating=random.randint(20, 40)
        self.is_intact=False
        self.respawn_timestamp=random.randint(1, 48)/48

    def update_telemetry(self, time_change):
        if self.is_break_released:
            self.align_speed(time_change)

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

    def change_train_layout(self, action, wagon_id_1):
        success=False
        if action=="A":
            self.train_layout[len(self.train_layout)]=wagon_id_1
            success=True
        elif action=="R" :
            for wg in self.train_layout:
                if self.config.conf_wagons[self.train_layout[wg]].base_id==wagon_id_1:
                    last=wg
                    success=True
            if success:
                del self.train_layout[last]
        elif action=="F":
            self.train_layout[wagon_id_1]=self.config.conf_wagons[self.train_layout[wagon_id_1]].base_id
            success=True
        elif action=="D":
            base_id=self.config.conf_wagons[self.train_layout[wagon_id_1]].base_id
            new_damage=self.config.conf_wagons[self.train_layout[wagon_id_1]].damage+1
            if new_damage<=3:
                for wagon_id in self.config.conf_wagons:
                    if self.config.conf_wagons[wagon_id].base_id==base_id and self.config.conf_wagons[wagon_id].damage==new_damage:
                        self.train_layout[wagon_id_1]=wagon_id
            success=True
        if success:             
            self.calculate_storage_cap()
        return success

    def change_cargo_manifest(self, action, item_id, price, qty):
        storage_type=self.config.conf_items[item_id].storage
        success=False
        if action=="A":
            if (self.storage_cap[storage_type]["max"]>=self.storage_cap[storage_type]["current"]+qty) and (self.cargo_manifest[self.get_item_id_from_name("Lignite")]["hold"]-price>=0):
                self.cargo_manifest[item_id]["value"]=self.cargo_manifest[item_id]["value"]*self.cargo_manifest[item_id]["hold"]+int(price)
                self.cargo_manifest[item_id]["hold"]=self.cargo_manifest[item_id]["hold"]+qty
                self.cargo_manifest[item_id]["value"]=self.cargo_manifest[item_id]["value"]/self.cargo_manifest[item_id]["hold"]
                self.storage_cap[storage_type]["current"]=self.storage_cap[storage_type]["current"]+qty
                if price != 0:
                    self.change_cargo_manifest("R", self.get_item_id_from_name("Lignite"), 0, price)
                success=True
        if action=="R":
            if (self.cargo_manifest[item_id]["hold"]-qty>=0) and (self.cargo_manifest[self.get_item_id_from_name("Lignite")]["hold"]+price<=self.storage_cap["coal"]["max"]):
                self.cargo_manifest[item_id]["hold"]=self.cargo_manifest[item_id]["hold"]-qty
                self.storage_cap[storage_type]["current"]=self.storage_cap[storage_type]["current"]-qty
                if price != 0:
                    self.change_cargo_manifest("A", self.get_item_id_from_name("Lignite"), 0, price)
                success=True
                if self.cargo_manifest[item_id]["hold"]==0:
                    self.cargo_manifest[item_id]["value"]=0    
        return success

    def get_item_id_from_name(self, item_name):
        for item_id in self.config.conf_items:
            if self.config.conf_items[item_id].item_name==item_name:
                return item_id
       
    def calculate_storage_cap(self):
        for storage_type in self.config.conf_storage_type:
            self.storage_cap[storage_type]["max"]=0
        for wg in self.train_layout:
            self.storage_cap[self.config.conf_wagons[self.train_layout[wg]].storage]["max"]=self.storage_cap[self.config.conf_wagons[self.train_layout[wg]].storage]["max"]+int(self.config.conf_wagons[self.train_layout[wg]].capacity)

    def count_wagon_with_id(self, wagon_id):
        count=0
        for wg in self.train_layout:
            if self.config.conf_wagons[self.train_layout[wg]].base_id==wagon_id:
                count += 1
        return count

    def calculate_force_value(self, engagement):
        force=0
        if engagement=="long_range":
            force+=self.storage_cap["shells"]["max"]//20
            force+=self.storage_cap["belts"]["max"]//10
            for item_id in self.cargo_manifest:
                if self.config.conf_items[item_id].storage in ["soldiers"]:
                    force+= int(self.cargo_manifest[item_id]["hold"])*int(self.config.conf_items[item_id].LRCV)
        if engagement=="short_range":
            force+=self.storage_cap["shells"]["max"]//5
            force+=self.storage_cap["belts"]["max"]//10
            for item_id in self.cargo_manifest:
                if self.config.conf_items[item_id].storage in ["soldiers","mammoths"]:
                    force+= int(self.cargo_manifest[item_id]["hold"])*int(self.config.conf_items[item_id].CQCV)
        return force

    def calculate_loot_loss(self, type, loot_perc):
        if type=="molemen":
            for item_id in self.cargo_manifest:
                if self.cargo_manifest[item_id]["hold"]>0:
                    self.cargo_manifest[item_id]["loss"]=0
                    for i in range(1, self.cargo_manifest[item_id]["hold"], 1):
                        if random.randint(1, 100)<loot_perc:
                            self.change_cargo_manifest("R", item_id, 0, 1)
                            self.cargo_manifest[item_id]["loss"]+=1
            return ""
        if type=="bridge_monster":
            for item_id in self.cargo_manifest:
                if self.cargo_manifest[item_id]["hold"]>0 and (self.config.conf_items[item_id].storage in ["soldiers", "mammoths", "slaves"] or self.config.conf_items[item_id].item_name in ["Meat"]) :
                    self.cargo_manifest[item_id]["loss"]=0
                    for i in range(1, self.cargo_manifest[item_id]["hold"], 1):
                        if random.randint(1, 100)<loot_perc:
                            self.change_cargo_manifest("R", item_id, 0, 1)
                            self.cargo_manifest[item_id]["loss"]+=1
            for wg in self.train_layout:
                if self.config.conf_wagons[self.train_layout[wg]].damage==0 and random.randint(1, 100)<loot_perc*2:
                   self.change_train_layout("D", wg, 0, 1, -1)
                   message="The train suffered some damage."
                if self.config.conf_wagons[self.train_layout[wg]].damage==1 and random.randint(1, 100)<loot_perc:
                   self.change_train_layout("D", wg, 0, 1, -1)
                   message="The train suffered some damage."
            return message

    def game_loaded(self, game_object):
        self.direction = game_object["direction"]
        self.is_in_reverse = game_object["is_in_reverse"]
        self.is_break_released = game_object["is_break_released"]
        self.speed = game_object["speed"]
        self.Speed_Regulator = game_object["Speed_Regulator"]
        self.target_speed = game_object["target_speed"]
        self.current_position = game_object["current_position"]
        self.force_rating = game_object["force_rating"]
        self.is_intact = game_object["is_intact"]
        self.respawn_timestamp = game_object["respawn_timestamp"]



    def current_timestamp(self):
        return director.core.timestamp