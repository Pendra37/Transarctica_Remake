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

class VUTrainActor(Sprite):
    """represents the player on the map"""
    velocity_multipliers = {"N": (0, 1), "B": (1, 1), "E": (1, 0),
                            "C": (1, -1), "S": (0, -1), "D": (-1, -1),
                            "W": (-1, 0), "A": (-1, 1)}
    opposites = {"N": "S", "B": "D", "E": "W", "C": "A", "S": "N", "D": "B",
                 "W": "E", "A": "C"}

    def __init__(self, map_manager,id):
        """initializer"""
        gallery = Gallery()
        self.rotation_vars = {}
        self.rotation_vars["NF"]={}
        self.rotation_vars["SR"]={}
        self.rotation_vars["BF"]={}
        self.rotation_vars["DR"]={}
        self.rotation_vars["EF"]={}
        self.rotation_vars["WR"]={}
        self.rotation_vars["CF"]={}
        self.rotation_vars["AR"]={}
        self.rotation_vars["SF"]={}
        self.rotation_vars["NR"]={}
        self.rotation_vars["DF"]={}
        self.rotation_vars["BR"]={}
        self.rotation_vars["WF"]={}
        self.rotation_vars["ER"]={}
        self.rotation_vars["AF"]={}
        self.rotation_vars["CR"]={}
        self.rotation_vars["BLANK"]={}

        self.rotation_vars["NF"]["sprite"]=gallery.content["actor"]["vuengine000"]
        self.rotation_vars["SR"]["sprite"]=gallery.content["actor"]["vuengine000"]
        self.rotation_vars["BF"]["sprite"]=gallery.content["actor"]["vuengine045"]
        self.rotation_vars["DR"]["sprite"]=gallery.content["actor"]["vuengine045"]
        self.rotation_vars["EF"]["sprite"]=gallery.content["actor"]["vuengine090"]
        self.rotation_vars["WR"]["sprite"]=gallery.content["actor"]["vuengine090"]
        self.rotation_vars["CF"]["sprite"]=gallery.content["actor"]["vuengine135"]
        self.rotation_vars["AR"]["sprite"]=gallery.content["actor"]["vuengine135"]
        self.rotation_vars["SF"]["sprite"]=gallery.content["actor"]["vuengine180"]
        self.rotation_vars["NR"]["sprite"]=gallery.content["actor"]["vuengine180"]
        self.rotation_vars["DF"]["sprite"]=gallery.content["actor"]["vuengine225"]
        self.rotation_vars["BR"]["sprite"]=gallery.content["actor"]["vuengine225"]
        self.rotation_vars["WF"]["sprite"]=gallery.content["actor"]["vuengine270"]
        self.rotation_vars["ER"]["sprite"]=gallery.content["actor"]["vuengine270"]
        self.rotation_vars["AF"]["sprite"]=gallery.content["actor"]["vuengine315"]
        self.rotation_vars["CR"]["sprite"]=gallery.content["actor"]["vuengine315"]
        self.rotation_vars["BLANK"]["sprite"]=gallery.content["switch"]["off"]
        
        self.rotation_vars["NF"]["smoke_angle"]=270
        self.rotation_vars["SR"]["smoke_angle"]=90
        self.rotation_vars["BF"]["smoke_angle"]=225
        self.rotation_vars["DR"]["smoke_angle"]=45
        self.rotation_vars["EF"]["smoke_angle"]=180
        self.rotation_vars["WR"]["smoke_angle"]=0
        self.rotation_vars["CF"]["smoke_angle"]=135
        self.rotation_vars["AR"]["smoke_angle"]=315
        self.rotation_vars["SF"]["smoke_angle"]=90
        self.rotation_vars["NR"]["smoke_angle"]=270
        self.rotation_vars["DF"]["smoke_angle"]=45
        self.rotation_vars["BR"]["smoke_angle"]=225
        self.rotation_vars["WF"]["smoke_angle"]=0
        self.rotation_vars["ER"]["smoke_angle"]=180
        self.rotation_vars["AF"]["smoke_angle"]=315
        self.rotation_vars["CR"]["smoke_angle"]=135
        self.rotation_vars["BLANK"]["smoke_angle"]=0

        self.rotation_vars["NF"]["smoke_pos"]= -2, 17 
        self.rotation_vars["SR"]["smoke_pos"]= -2, 17 
        self.rotation_vars["BF"]["smoke_pos"]=  1, 26 
        self.rotation_vars["DR"]["smoke_pos"]=  1, 26 
        self.rotation_vars["EF"]["smoke_pos"]= 18, 17 
        self.rotation_vars["WR"]["smoke_pos"]= 18, 17 
        self.rotation_vars["CF"]["smoke_pos"]= 25, -1 
        self.rotation_vars["AR"]["smoke_pos"]= 25, -1 
        self.rotation_vars["SF"]["smoke_pos"]= -2,-17 
        self.rotation_vars["NR"]["smoke_pos"]= -2,-17 
        self.rotation_vars["DF"]["smoke_pos"]=-26, -2 
        self.rotation_vars["BR"]["smoke_pos"]=-26, -2 
        self.rotation_vars["WF"]["smoke_pos"]=-18, 17 
        self.rotation_vars["ER"]["smoke_pos"]=-18, 17 
        self.rotation_vars["AF"]["smoke_pos"]= -5, 30 
        self.rotation_vars["CR"]["smoke_pos"]= -5, 30 
        self.rotation_vars["BLANK"]["smoke_pos"]=-18, 17

        self.is_moving=False
        Sprite.__init__(self, self.rotation_vars["BLANK"]["sprite"])
        self.counter=0
        self.map = map_manager
        self.vutrain = director.core.query_mover("VUTrain"+str(id))
        self.ID=id
        self.transarctica = director.core.query_mover("Transarctica")
        self.driver = TrainDriver()
        self.driver.target = self
        self.config = Config()
        self.anchor = self.config.tile_width/2, self.config.tile_width/2
        #self.spawn_randomly()
        self.last_position = {"X":self.vutrain.current_position["X"], "Y":self.vutrain.current_position["Y"]}
        self.max_forward_speed = 450 / self.config.km_per_tile * self.config.tile_width / 3600
        self.position = (-1, -1)
        self.last_break_status = self.vutrain.is_break_released
        self.last_reverse_status = self.vutrain.is_in_reverse
        self.last_direction = self.vutrain.direction
        self.arriving_from=""
        self.leaving_toward=""
        self.on_tile="none"
        self.next_turn_at = (-1, -1)
        self.tile_entry_point = (-1, -1)
        self.visible=False

        self.smoke=Smoke()
        self.smoke.blend_additive=False
        self.smoke.position=self.rotation_vars["NF"]["smoke_pos"] 
        self.smoke.life=1
        self.smoke.speed=30
        self.smoke.start_color = Color(0.1, 0.1, 0.1, 0.8) 
        self.smoke.size = 15.0
        self.smoke.total_particles=40
        self.add(self.smoke)
        self.prev_dirs=""


    def update_actor(self, dt):
        if self.last_break_status!=self.vutrain.is_break_released:
            self.last_break_status=self.vutrain.is_break_released
            if self.vutrain.is_break_released:
                self.start()
            else:
                self.stop()

        if (self.last_position["X"]!=self.vutrain.current_position["X"] or self.last_position["Y"]!=self.vutrain.current_position["Y"]) or (self.last_reverse_status!=self.vutrain.is_in_reverse):
            cell = self.map.get("rails").cells[self.vutrain.current_position["X"]][self.vutrain.current_position["Y"]]
            if (self.last_reverse_status!=self.vutrain.is_in_reverse):
                self.turn_back()

            if cell.tile:
                self.vutrain.Speed_Modifier = 1
                if (("speedmod" in cell.properties) and ("tunneldir" not in cell.properties)) or (("tunneldir" in cell.properties) and (self.vutrain.direction in cell.properties["tunneldir"])):
                    self.vutrain.Speed_Modifier = float(cell.properties["speedmod"])
                if (self.last_position["X"]!=self.vutrain.current_position["X"] or self.last_position["Y"]!=self.vutrain.current_position["Y"]):
                    self.tile_entry_point = self.position
                self.next_turn_at = (-1, -1)
                if "nodes" in cell.properties: 
                    self.arriving_from=self.opposites[self.vutrain.direction]
                    self.leaving_toward=cell.properties["directions"]
                    if len(self.leaving_toward)==1:
                        self.on_tile="bumper"
                        self.leaving_toward=self.arriving_from
                    elif len(self.leaving_toward)==2:
                        self.on_tile="normal"
                        self.leaving_toward=self.leaving_toward.replace(self.arriving_from, "")
                    elif len(self.leaving_toward)==3:
                        if self.leaving_toward[0]!=self.arriving_from:
                            self.leaving_toward=self.leaving_toward[0]
                            self.on_tile="normal"
                        else:
                            self.leaving_toward=self.leaving_toward[random.randint(1, 2)]
                            self.on_tile="switch"
                    elif len(self.leaving_toward)==5:
                        self.on_tile="cross"
                        self.leaving_toward=self.opposites[self.arriving_from]
 
                    if (self.leaving_toward!= self.opposites[self.arriving_from]) and (self.next_turn_at == (-1,-1)): 
                        rails = self.map.get("hidden objects")
                        self.next_turn_at = rails.cells[self.vutrain.current_position["X"]][self.vutrain.current_position["Y"]].center
                
                map_event=self.map.check_map_events_vutrain(self.vutrain.current_position["X"], self.vutrain.current_position["Y"])
                if map_event in ["bridge_out", "end_of_rail"]:
                    self.vutrain.current_position["X"]=self.last_position["X"]
                    self.vutrain.current_position["Y"]=self.last_position["Y"]
                    self.vutrain.is_in_reverse = not(self.vutrain.is_in_reverse)
                    self.map.place_vutrain(self.ID)

                self.last_position["X"]=self.vutrain.current_position["X"]
                self.last_position["Y"]=self.vutrain.current_position["Y"]
                self.last_direction = self.vutrain.direction
            else:
                self.vutrain.current_position["X"]=self.last_position["X"]
                self.vutrain.current_position["Y"]=self.last_position["Y"]
                self.map.place_vutrain(self.ID)
        
        if self.visible:
            if self.vutrain.is_in_reverse:
                dirs=self.vutrain.direction+"R"
            else:
                dirs=self.vutrain.direction+"F"
         
            if self.prev_dirs!=dirs:
                self.image=self.rotation_vars[dirs]["sprite"]
                self.smoke.position=self.rotation_vars[dirs]["smoke_pos"] 
                self.prev_dirs=dirs
            
            if self.vutrain.speed==0:
                self.smoke.angle=self.rotation_vars["SF"]["smoke_angle"]
            else:    
                self.smoke.angle=self.rotation_vars[dirs]["smoke_angle"] 
                self.smoke.speed=(self.vutrain.speed//10)+10  
            
            if (self.vutrain.Speed_Modifier > 1):
                self.smoke.total_particles=0
                self.counter=(self.counter+1)%30 
                if (self.counter == 15):
                    self.image=self.rotation_vars["BLANK"]["sprite"]
                elif self.counter == 0:
                   self.prev_dirs="BLANK"  
            else:
                self.smoke.total_particles=40 
         
        dist=self.distance_from_transarctica(self.transarctica.vis_range)
        if dist<self.transarctica.vis_range:   
            self.visible=True 
            if dist<10:   
                self.transarctica.proximity_alarm+=1
            self.prev_dirs=""  
            if self.vutrain.current_position["X"]==self.transarctica.current_position["X"] and self.vutrain.current_position["Y"]==self.transarctica.current_position["Y"]:
                self.vutrain.is_intact=False
                self.vutrain.respawn_timestamp=director.core.timestamp+(random.randint(15,30)/10)
                self.image=self.rotation_vars["BLANK"]["sprite"]
                self.smoke.total_particles=0 
                self.transarctica.speed=0
                self.transarctica.is_break_released=False
                self.transarctica.opfor_id=self.ID
                events.emit_show_event("display_event_train_combat") 
                self.vutrain.force_rating=self.vutrain.force_rating*2
        else:
            self.visible=False 
            self.image=self.rotation_vars["BLANK"]["sprite"]
            self.smoke.total_particles=0 

        if self.is_moving:
            self.move(dt)

    def move(self, dt):
        current_cell = self.map.get("rails").get_at_pixel(*self.position)
        self.vutrain.current_position = {"X": current_cell.i, "Y": current_cell.j}
        self.driver.step_vutrain(dt)

    def get_distance_between_points(self, start_point, end_point):
        """:returns distance: in pixel"""
        x_distance = end_point[0] - start_point[0]
        y_distance = end_point[1] - start_point[1]
        return sqrt(x_distance**2 + y_distance**2)

    def convert_progression_to_direction_vectors(self, progress):
        """
        self.driver calls this method to get the required direction modifiers.
        :param progress:
        :return: tuple of X and Y progression
        """
        is_direction_diagonal = self.vutrain.direction in ["A", "B", "C", "D"]
        if is_direction_diagonal:
            progress = sqrt((progress**2)/2)
        horizontal_progression = self.velocity_multipliers[self.vutrain.direction][0] * progress
        vertical_progression = self.velocity_multipliers[self.vutrain.direction][1] * progress
        return horizontal_progression, vertical_progression

    def get_speed(self):
        """:returns current speed: in pixel/sec"""
        speed_in_pixel_per_seconds = self.vutrain.speed / self.config.km_per_tile * self.config.tile_width / 30 #self.config.simulation_speed
        return speed_in_pixel_per_seconds * self.config.time_speed

    def start(self):
        self.is_moving=True
        self.vutrain.is_break_released=True

    def stop(self):
        self.is_moving=False
        self.vutrain.speed=0
        self.vutrain.is_break_released=False

    def turn_back(self):
        if self.vutrain.is_in_reverse:
            self.reverse()
        else:
            self.forward()
        self.last_reverse_status=self.vutrain.is_in_reverse

    def forward(self):
        self.vutrain.direction = self.opposites[self.vutrain.direction]
        self.vutrain.speed=0
        self.vutrain.is_in_reverse=False

    def reverse(self):
        self.vutrain.direction = self.opposites[self.vutrain.direction]
        self.vutrain.speed=0
        self.vutrain.is_in_reverse=True

    def city_bumper_hit(self):
        A=1

    def distance_from_transarctica(self, E):
        if abs(self.vutrain.current_position["X"]-self.transarctica.current_position["X"]<E) and abs(self.vutrain.current_position["Y"]-self.transarctica.current_position["Y"]<E):
            return sqrt(pow(self.vutrain.current_position["X"]-self.transarctica.current_position["X"],2)+pow(self.vutrain.current_position["Y"]-self.transarctica.current_position["Y"],2))
        else:
            return 9999  

    def place_randomly(self):
        placed=False
        while not(placed):
            x = random.randint(5, self.config.map_width-5)
            y = random.randint(5, self.config.map_height-5)
            cell = self.map.get("rails").cells[x_id][y_id]
            if cell.tile:
                self.vutrain.current_position["X"]=x
                self.vutrain.current_position["Y"]=y
                self.vutrain.direction = cell.properties["directions"]
                self.vutrain.direction = self.vutrain.direction[0]
                placed=True

    def spawn_randomly(self):
        if self.vutrain.respawn_timestamp < director.core.timestamp:
            start_pos_id=random.randint(0, len(self.config.vu_start_positions)-1)
            self.vutrain.current_position["X"] = self.config.vu_start_positions[start_pos_id]["X"]
            self.vutrain.current_position["Y"] = self.config.vu_start_positions[start_pos_id]["Y"]
            self.vutrain.direction = self.config.vu_start_positions[start_pos_id]["D"]
            self.vutrain.is_intact = True
            self.map.place_vutrain(self.ID)

    @property
    def is_break_released(self):
        return self.vutrain.is_break_released

    @property
    def is_in_reverse(self):
        return self.vutrain.is_in_reverse

