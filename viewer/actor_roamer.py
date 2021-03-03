# -*- coding: utf-8 -*-
from . import Gallery
from .traindriver import TrainDriver
from controller import events
from cocos.director import director
from cocos.sprite import Sprite
from math import sqrt
from model import Config
import random
from cocos.particle_systems import Smoke
from cocos.particle import Color

class RoamerActor(Sprite):
    velocity_multipliers = {"N": (0, 1), "B": (1, 1), "E": (1, 0),
                            "C": (1, -1), "S": (0, -1), "D": (-1, -1),
                            "W": (-1, 0), "A": (-1, 1)}

    def __init__(self, map_manager,id):
        """initializer"""
        gallery = Gallery()
        self.rotation_vars = {}
        self.rotation_vars["nomads"]={}
        self.rotation_vars["mammoth_herd"]={}
        self.rotation_vars["BLANK"]={}

        self.rotation_vars["BLANK"]["sprite"]=gallery.content["switch"]["off"]
        self.rotation_vars["nomads"]["sprite"]=gallery.content["actor"]["nomads"]
        self.rotation_vars["mammoth_herd"]["sprite"]=gallery.content["actor"]["mammoth_herd"]

        Sprite.__init__(self, self.rotation_vars["BLANK"]["sprite"])
        self.counter=0
        self.map = map_manager
        self.roamer = director.core.query_mover("Roamer"+str(id))
        self.ID=id
        self.transarctica = director.core.query_mover("Transarctica")
        self.driver = TrainDriver()
        self.driver.target = self
        self.config = Config()
        self.anchor = self.config.tile_width/2, self.config.tile_width/2
        self.next_update=0
        self.max_forward_speed = 100 / self.config.km_per_tile * self.config.tile_width / 3600

    def update_actor(self, dt):
        if (self.roamer.current_position["X"] < 4) or  (self.roamer.current_position["X"] > self.config.map_width-4) or (self.roamer.current_position["Y"] < 4) or (self.roamer.current_position["Y"] > self.config.map_height-4):
            self.roamer.current_position["X"] = random.randint(5, self.config.map_width-5)
            self.roamer.current_position["Y"] = random.randint(5, self.config.map_height-5)
            self.map.place_roamer(self.ID)
        if self.next_update<director.core.timestamp:
            self.roamer.direction=self.roamer.directions[random.randint(0, len(self.roamer.directions)-1)]  
            self.next_update=director.core.timestamp+(0.066/random.randint(1, 3))
        dist=self.distance_from_transarctica(self.transarctica.vis_range)
        if dist<self.transarctica.vis_range:   
            if dist<10:   
                self.transarctica.proximity_alarm+=1
            self.image=self.rotation_vars[self.roamer.roamer_type]["sprite"]
            if self.roamer.current_position["X"]==self.transarctica.current_position["X"] and self.roamer.current_position["Y"]==self.transarctica.current_position["Y"]:
                self.transarctica.is_break_released=False
                self.transarctica.opfor_id=self.ID
                events.emit_show_event("display_event_"+self.roamer.roamer_type) 
                self.roamer.current_position["X"] = random.randint(5, self.config.map_width-5)
                self.roamer.current_position["Y"] = random.randint(5, self.config.map_height-5)
                self.map.place_roamer(self.ID)
        else:
            self.image=self.rotation_vars["BLANK"]["sprite"]
        self.move(dt)

    def move(self, dt):
        current_cell = self.map.get("rails").get_at_pixel(*self.position)
        self.roamer.current_position = {"X": current_cell.i, "Y": current_cell.j}
        self.driver.step_roamer(dt)


    def distance_from_transarctica(self, E):
        if abs(self.roamer.current_position["X"]-self.transarctica.current_position["X"]<E) and abs(self.roamer.current_position["Y"]-self.transarctica.current_position["Y"]<E):
            return sqrt(pow(self.roamer.current_position["X"]-self.transarctica.current_position["X"],2)+pow(self.roamer.current_position["Y"]-self.transarctica.current_position["Y"],2))
        else:
            return 9999  

    def convert_progression_to_direction_vectors(self, progress):
        """
        self.driver calls this method to get the required direction modifiers.
        :param progress:
        :return: tuple of X and Y progression
        """
        if self.roamer.direction in ["A", "B", "C", "D"]:
            progress = sqrt((progress**2)/2)
        horizontal_progression = self.velocity_multipliers[self.roamer.direction][0] * progress
        vertical_progression = self.velocity_multipliers[self.roamer.direction][1] * progress
        return horizontal_progression, vertical_progression

    def get_speed(self):
        """:returns current speed: in pixel/sec"""
        speed_in_pixel_per_seconds = self.roamer.speed / self.config.km_per_tile * self.config.tile_width / 30 #self.config.simulation_speed
        return speed_in_pixel_per_seconds * self.config.time_speed

    def start(self):
        """starts train"""
        self.roamer.is_break_released=True

    def stop(self):
        """stops the train movement but maintains current speed data"""
        self.roamer.is_break_released=False

    @property
    def is_break_released(self):
        return self.roamer.is_break_released
