# -*- coding: utf-8 -*-
from . import Gallery
from .traindriver import TrainDriver
from controller import events
from cocos.director import director
from cocos.sprite import Sprite
from math import sqrt
from model import Config
from cocos.particle_systems import Smoke
from cocos.particle import Color
from pyglet.media import load
from pyglet.media import Player, SourceGroup

class TransarcticaActor(Sprite):
    """represents the player on the map"""
    velocity_multipliers = {"N": (0, 1), "B": (1, 1), "E": (1, 0),
                            "C": (1, -1), "S": (0, -1), "D": (-1, -1),
                            "W": (-1, 0), "A": (-1, 1)}
    opposites = {"N": "S", "B": "D", "E": "W", "C": "A", "S": "N", "D": "B",
                 "W": "E", "A": "C"}

    def __init__(self, map_manager):
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

        self.rotation_vars["NF"]["sprite"]=gallery.content["actor"]["engine000"]
        self.rotation_vars["SR"]["sprite"]=gallery.content["actor"]["engine000"]
        self.rotation_vars["BF"]["sprite"]=gallery.content["actor"]["engine045"]
        self.rotation_vars["DR"]["sprite"]=gallery.content["actor"]["engine045"]
        self.rotation_vars["EF"]["sprite"]=gallery.content["actor"]["engine090"]
        self.rotation_vars["WR"]["sprite"]=gallery.content["actor"]["engine090"]
        self.rotation_vars["CF"]["sprite"]=gallery.content["actor"]["engine135"]
        self.rotation_vars["AR"]["sprite"]=gallery.content["actor"]["engine135"]
        self.rotation_vars["SF"]["sprite"]=gallery.content["actor"]["engine180"]
        self.rotation_vars["NR"]["sprite"]=gallery.content["actor"]["engine180"]
        self.rotation_vars["DF"]["sprite"]=gallery.content["actor"]["engine225"]
        self.rotation_vars["BR"]["sprite"]=gallery.content["actor"]["engine225"]
        self.rotation_vars["WF"]["sprite"]=gallery.content["actor"]["engine270"]
        self.rotation_vars["ER"]["sprite"]=gallery.content["actor"]["engine270"]
        self.rotation_vars["AF"]["sprite"]=gallery.content["actor"]["engine315"]
        self.rotation_vars["CR"]["sprite"]=gallery.content["actor"]["engine315"]
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
        self.transarctica = director.core.query_mover("Transarctica")
        self.transarctica.map = map_manager
        self.driver = TrainDriver()
        self.driver.target = self
        self.config = Config()
        self.break_sound_source = load('music/stop.wav')#, streaming=False)
        #self.break_sound.volume=0.5 * self.config.sound_switch





        self.anchor = self.config.tile_width/2, self.config.tile_width/2
        #self.transarctica.current_position = self.config.start_position
        self.last_position = {"X":self.transarctica.current_position["X"], "Y":self.transarctica.current_position["Y"]}
        self.max_forward_speed = 450 / self.config.km_per_tile * self.config.tile_width / 3600
        self.position = (-1, -1)
        self.last_break_status = self.transarctica.is_break_released
        self.last_reverse_status = self.transarctica.is_in_reverse
        self.last_direction = self.transarctica.direction
        self.arriving_from=""
        self.leaving_toward=""
        self.on_tile="none"
        self.next_turn_at = (-1, -1)
        self.tile_entry_point = (-1, -1)
        
        self.smoke=Smoke()
        self.smoke.blend_additive=False
        self.smoke.position=self.rotation_vars["NF"]["smoke_pos"] 
        self.smoke.life=1
        self.smoke.speed=30
        self.smoke.start_color = Color(0.20, 0.20, 0.20, 0.40) 
        self.smoke.size = 15.0
        self.smoke.total_particles=60
        self.add(self.smoke)
        self.prev_dirs=""

    def update_actor(self, dt):
        self.transarctica.proximity_alarm=0
        if self.last_break_status!=self.transarctica.is_break_released:
            self.last_break_status=self.transarctica.is_break_released
            if self.transarctica.is_break_released:
                self.start()
            else:
                self.stop()

        if (self.last_position["X"]!=self.transarctica.current_position["X"] or self.last_position["Y"]!=self.transarctica.current_position["Y"]) or (self.last_reverse_status!=self.transarctica.is_in_reverse):
            cell = self.map.get("rails").cells[self.transarctica.current_position["X"]][self.transarctica.current_position["Y"]]
            if (self.last_reverse_status!=self.transarctica.is_in_reverse):
                self.turn_back()

            if cell.tile:
                self.transarctica.Speed_Modifier = 1
                if (("speedmod" in cell.properties) and ("tunneldir" not in cell.properties)) or (("tunneldir" in cell.properties) and (self.transarctica.direction in cell.properties["tunneldir"])):
                    self.transarctica.Speed_Modifier = float(cell.properties["speedmod"])
                if (self.last_position["X"]!=self.transarctica.current_position["X"] or self.last_position["Y"]!=self.transarctica.current_position["Y"]):
                    self.tile_entry_point = self.position
                self.next_turn_at = (-1, -1)
                if "nodes" in cell.properties: 
                    self.arriving_from=self.opposites[self.transarctica.direction]
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
                            self.leaving_toward=self.leaving_toward[1]
                            self.on_tile="switch"
                    elif len(self.leaving_toward)==5:
                        self.on_tile="cross"
                        self.leaving_toward=self.opposites[self.arriving_from]
 
                    if (self.leaving_toward!= self.opposites[self.arriving_from]) and (self.next_turn_at == (-1,-1)): 
                        rails = self.map.get("hidden objects")
                        self.next_turn_at = rails.cells[self.transarctica.current_position["X"]][self.transarctica.current_position["Y"]].center
                
                map_event=self.map.check_map_events(self.transarctica.current_position["X"], self.transarctica.current_position["Y"])
                if map_event in ["tunnel_block", "bridge_monster"]:
                    self.stop()
                    self.start()
                    events.emit_show_event("display_event_"+map_event)
                elif map_event in ["arrive_at_city"]:
                    self.on_tile="city_bumper"
                elif map_event in ["bridge_out"]:
                    self.stop()
                    self.start()
                    events.emit_show_event("display_event_build_bridge")
                    self.transarctica.current_position["X"]=self.last_position["X"]
                    self.transarctica.current_position["Y"]=self.last_position["Y"]
                    self.transarctica.is_in_reverse = not(self.transarctica.is_in_reverse)
                    self.transarctica.is_break_released = not(self.transarctica.is_break_released)
                    self.map.place_player()
                elif map_event in ["end_of_rail"]:
                    self.stop()
                    self.start()
                    self.transarctica.current_position["X"]=self.last_position["X"]
                    self.transarctica.current_position["Y"]=self.last_position["Y"]
                    self.transarctica.is_in_reverse = not(self.transarctica.is_in_reverse)
                    self.transarctica.is_break_released = not(self.transarctica.is_break_released)
                    self.map.place_player()

                self.last_position["X"]=self.transarctica.current_position["X"]
                self.last_position["Y"]=self.transarctica.current_position["Y"]
                self.last_direction = self.transarctica.direction
            else:
                map_event=self.map.check_map_events(self.transarctica.current_position["X"], self.transarctica.current_position["Y"])
                if map_event in ["arrive_at_city"]:
                    self.service_bumper_hit()

                self.transarctica.current_position["X"]=self.last_position["X"]
                self.transarctica.current_position["Y"]=self.last_position["Y"]
                self.map.place_player()

        if self.transarctica.is_in_reverse:
            dirs=self.transarctica.direction+"R"
        else:
            dirs=self.transarctica.direction+"F"

        if self.prev_dirs!=dirs:
            self.image=self.rotation_vars[dirs]["sprite"]
            self.smoke.position=self.rotation_vars[dirs]["smoke_pos"] 
            self.prev_dirs=dirs
        
        if self.transarctica.speed==0:
            self.smoke.angle=self.rotation_vars["SF"]["smoke_angle"]
        else:    
            self.smoke.angle=self.rotation_vars[dirs]["smoke_angle"] 
            self.smoke.speed=(self.transarctica.speed//10)+10  
        
        if (self.transarctica.Speed_Modifier > 1):
            self.smoke.total_particles=0
            self.counter=(self.counter+1)%30 
            if (self.counter == 15):
                self.image=self.rotation_vars["BLANK"]["sprite"]
            elif self.counter == 0:
               self.prev_dirs="BLANK"  
        else:
            self.smoke.total_particles=60 
        self.smoke.start_color = Color(0.10, 0.10, 0.10, max(min(1,self.transarctica.engine_temp/600),0.01)) 
        if self.is_moving:
            self.move(dt)

    def move(self, dt):
        current_cell = self.map.get("rails").get_at_pixel(*self.position)
        self.transarctica.current_position = {"X": current_cell.i, "Y": current_cell.j}
        self.driver.step_transarctica(dt)

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
        is_direction_diagonal = self.transarctica.direction in ["A", "B", "C", "D"]
        if is_direction_diagonal:
            progress = sqrt((progress**2)/2)
        horizontal_progression = self.velocity_multipliers[self.transarctica.direction][0] * progress
        vertical_progression = self.velocity_multipliers[self.transarctica.direction][1] * progress
        return horizontal_progression, vertical_progression

    def get_speed(self):
        """:returns current speed: in pixel/sec"""
        #time_multiplier = (self.config.simulation_speed * 50)* self.config.time_speed
        #speed_in_pixel_per_seconds = self.transarctica.speed / self.config.km_per_tile * self.config.tile_width / 3600
        speed_in_pixel_per_seconds = self.transarctica.speed / self.config.km_per_tile * self.config.tile_width / 30 #self.config.simulation_speed
        return speed_in_pixel_per_seconds * self.config.time_speed

    def play_sound_once(self,soundfile,volume):
        if self.config.sound_switch>0:
            play_sound = Player()
            play_sound_source = load(soundfile)
            play_sound_group = SourceGroup(play_sound_source.audio_format, None)
            play_sound_group.loop = False
            play_sound_group.queue(play_sound_source)
            play_sound.queue(play_sound_group)
            play_sound.volume=float(volume) * self.config.sound_switch
            play_sound.play()

    def start(self):
        self.is_moving=True
        self.transarctica.is_break_released=True
        self.map.parent.get("display_worldmap_hud").switch_break()

    def stop(self):
        self.play_sound_once('music/stop.wav',0.6)
        self.is_moving=False
        self.transarctica.speed=0
        self.transarctica.is_break_released=False
        self.map.parent.get("display_worldmap_hud").switch_break()

    def turn_back(self):
        if self.transarctica.is_in_reverse:
            self.reverse()
        else:
            self.forward()
        self.last_reverse_status=self.transarctica.is_in_reverse

    def forward(self):
        self.transarctica.direction = self.opposites[self.transarctica.direction]
        self.transarctica.speed=0
        self.transarctica.is_in_reverse=False
        self.map.parent.get("display_worldmap_hud").switch_direction()

    def reverse(self):
        self.transarctica.direction = self.opposites[self.transarctica.direction]
        self.transarctica.speed=0
        self.transarctica.is_in_reverse=True
        self.map.parent.get("display_worldmap_hud").switch_direction()

    def service_bumper_hit(self):
        self.stop()
        self.start()
        self.transarctica.is_in_reverse = not(self.transarctica.is_in_reverse)
        events.emit_show_city(self.map.get("rails").cells[self.transarctica.current_position["X"]][self.transarctica.current_position["Y"]].properties["city"])

    def city_bumper_hit(self):
        events.emit_show_city(self.map.get("rails").cells[self.transarctica.current_position["X"]][self.transarctica.current_position["Y"]].properties["city"])

    @property
    def is_break_released(self):
        return self.transarctica.is_break_released

    @property
    def is_in_reverse(self):
        return self.transarctica.is_in_reverse