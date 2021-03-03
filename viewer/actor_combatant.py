# -*- coding: utf-8 -*-
from . import Gallery
from .traindriver import TrainDriver
from controller import events
from cocos.director import director
from cocos.sprite import Sprite
from math import sqrt
from model import Config
from cocos.draw import Line
from math import trunc
import random
from cocos.particle_systems import Smoke
from cocos.particle_systems import Fire
from cocos.particle_systems import Sun
from cocos.particle import Color



from cocos.particle import Color

class ActorCombatant(Sprite):
    velocity_multipliers = {"N": (0, 1), "B": (1, 1), "E": (1, 0), "C": (1, -1), "S": (0, -1), "D": (-1, -1), "W": (-1, 0), "A": (-1, 1)}
    moveto_direction = {"0/1":"N", "1/1":"B", "1/0":"E", "1/-1":"C", "0/-1":"S", "-1/-1":"D", "-1/0":"W", "-1/1":"A"}

    def __init__(self, map_manager, combatant, side):
        """initializer"""
        gallery = Gallery()
        self.c_stats={}
        self.config = Config()
        self.load_c_stats(gallery)
        self.side=side
        self.combatant=combatant

        Sprite.__init__(self, gallery.content["switch"]["off"])
        self.map = map_manager

        self.anchor = self.map.get("combat").tw/2, self.map.get("combat").tw/2
        self.direction="W"
        self.prev_dist=9999
        self.start_dist=-1
        self.start_tile=(-1, -1)
        self.right_tx=-1
        self.left_tx=-1
        self.total_width=0
        self.move_speed=192 #pixel/sec
        self.slowdown_rate=1
        self.tw=64
        self.wagons=[]
        self.wagons_decals=[]
        self.wagon_id=-1
        self.wagon_width=-1
        if combatant.find("combat_train")<0:
            self.stat=self.c_stats[self.combatant+self.side]
            self.group_size=random.randint(1, self.stat["max_group_size"])
            self.force=self.group_size*self.stat["base_force_per"]
            self.line_force_ind = Line((-30,28), (-30+(30*2),28), (0, 0, 255, 255),2)
            self.calc_force_color(self.line_force_ind,self.force,1)
            self.add(self.line_force_ind, name="line_temp_ind")
        self.move_done=True


    def place_train(self,tx,ty):
        self.x=tx*self.tw
        self.y=ty*self.tw
        self.left_tx=tx
        self.right_tx=tx
    
    def set_visible(self,vis):
        gallery = Gallery()
        if vis:
            self.image=self.stat["sprite"]
        else:
            self.image=gallery.content["switch"]["off"] 


    def add_wagon(self,rank,wagon_type):
        wagon=Sprite(self.c_stats[wagon_type+self.side]["sprite"] )
        wagon.image_anchor = self.image_anchor
        wagon.scale = 1
        self.left_tx-=wagon.width//self.tw
        self.total_width+=wagon.width
        wagon.x = -self.total_width
        wagon.y = 0
        self.add(wagon)

    def add_wagon_b(self,wagon_type, wforce):
        wagon=Sprite(self.c_stats[wagon_type+self.side]["sprite"] )
        wagon.image_anchor = self.image_anchor
        wagon.scale = 1
        self.left_tx-=wagon.width//self.tw
        self.total_width+=wagon.width
        wagon.x = -self.total_width
        wagon.y = 0
        self.add(wagon)
        if wagon.width>100:
            hp_bar_size=100
        else:
            hp_bar_size=50
        padding=(wagon.width-hp_bar_size)//2
        line_force_ind = Line((padding,15), (padding+wforce,15), (0, 0, 255, 255),2)
        self.calc_force_color(line_force_ind, wforce, 2)

        wagon.add(line_force_ind, name="line_force_ind")
        self.wagons.append(wagon)
        return (wagon.width//self.tw, len(self.wagons)-1)

    def wagon_damaged(self, wid, wwidth, wforce):
        gallery = Gallery()
        wagon=self.wagons[wid]
        if wagon.width>100:
            hp_bar_size=100
        else:
            hp_bar_size=50
        padding=(wagon.width-hp_bar_size)//2
        line_force_ind=wagon.get("line_force_ind")
        line_force_ind.end=(padding+wforce,15)
        self.calc_force_color(line_force_ind, wforce, 2)

        if wforce<=0:
            wagon.image=gallery.content["trn"]["wreck"+str(wwidth)+self.side]
            line_force_ind.end=line_force_ind.start

    def recalculate_force(self, delta_force):
        delta_group_size = delta_force // self.stat["base_force_per"]
        self.group_size+=delta_group_size
        self.force=self.group_size*self.stat["base_force_per"]
        self.line_force_ind.end=(-30+(self.force*2),28)
        self.calc_force_color(self.line_force_ind,self.force,1)

    def calc_force_color(self, line_force_ind, force, multiplier):
        if force<10*multiplier:
            line_force_ind.color= (255, 0, 0, 255)
        elif force<20*multiplier:
            line_force_ind.color= (255, 255, 0, 255)
        else:
            line_force_ind.color= (0, 255, 0, 255)

    def move_train(self, dist, dest_tile, moveit):
        self.move_done=False
        if dist>0:
            self.direction="E"
        else:
            self.direction="W"
        self.target_tile=dest_tile
        if moveit:
            self.schedule(self.step_train)
        else:
            self.unschedule(self.step_train)
            self.move_done=True

    def step_train(self, dt):
        if (self.prev_dist<self.tw) or (self.start_dist-self.prev_dist<self.tw) :
            self.slowdown_rate=2
        else:
            self.slowdown_rate=1
        step = dt * (self.move_speed/self.slowdown_rate)
        delta = self.convert_progression_to_direction_vectors(step)
        self.position = (self.position[0] + delta[0], self.position[1] + delta[1])
        dist=self.get_distance_between_points(self.position,self.midleft(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]]))
        if self.start_dist<0:
            self.start_dist=dist
        if dist<=self.prev_dist:
            self.prev_dist=dist
        else:
            self.unschedule(self.step_train)
            self.move_done=True
            ppos=self.midleft(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]])   
            self.prev_dist=9999
            self.start_dist=-1

    def midleft(self, tile):
        return (tile.left,tile.center[1])

    def move_unit_blocked(self, path, moveit):
        self.move_path=path
        self.move_unit(self.move_path[0], self.move_path[1] ,True)

    def move_unit(self, start_tile, dest_tile, moveit):
        self.move_done=False
        self.direction=self.moveto_direction[str(dest_tile[0]-start_tile[0])+"/"+str(dest_tile[1]-start_tile[1])]
        self.target_tile=dest_tile
        if moveit:
            self.schedule(self.step_unit)
        else:
            self.unschedule(self.step_unit)
            self.move_done=True

    def step_unit(self, dt):
        step = dt * self.move_speed
        delta = self.convert_progression_to_direction_vectors(step)
        self.position = (self.position[0] + delta[0], self.position[1] + delta[1])
        dist=self.get_distance_between_points(self.position,self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].center)
        if dist<=self.prev_dist:
            self.prev_dist=dist
        else:
            self.unschedule(self.step_unit)
            self.move_done=True
            self.position=self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].center
            self.prev_dist=9999
            if len(self.move_path)>2:
                self.move_path.pop(0)
                self.move_unit(self.move_path[0], self.move_path[1] ,True)
            else:
                self.move_path.clear()



    def get_distance_between_points(self, start_point, end_point):
        x_distance = end_point[0] - start_point[0]
        y_distance = end_point[1] - start_point[1]
        return sqrt(x_distance**2 + y_distance**2)

    def convert_progression_to_direction_vectors(self, progress):
        if self.direction in ["A", "B", "C", "D"]:
            progress = sqrt((progress**2)/2)
        horizontal_progression = self.velocity_multipliers[self.direction][0] * progress
        vertical_progression = self.velocity_multipliers[self.direction][1] * progress
        return horizontal_progression, vertical_progression

    def load_c_stats(self,gallery):

        self.c_stats["s01_tr"]={}
        self.c_stats["s01_tr"]["name"]="Soldier"
        self.c_stats["s01_tr"]["max_move"]=3
        self.c_stats["s01_tr"]["max_range"]=1
        self.c_stats["s01_tr"]["move_modifiers"] ={"open":1, "rail":99, "h":99, "l":99, "f":2}
        self.c_stats["s01_tr"]["max_group_size"]=15
        self.c_stats["s01_tr"]["base_force_per"]=2
        self.c_stats["s01_tr"]["sprite"]=gallery.content["trn"]["s01"]
        self.c_stats["s01_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(-5,5), "close":(0,0), "ranged":(0,0)}
        self.c_stats["s01_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,10), "close":(0,0), "ranged":(0,0) }
        self.c_stats["s01_tr"]["spawn"]="na"
        self.c_stats["s01_tr"]["type"]="unit"

        self.c_stats["s02_tr"]={}
        self.c_stats["s02_tr"]["name"]="Ranger"
        self.c_stats["s02_tr"]["max_move"]=2
        self.c_stats["s02_tr"]["max_range"]=4
        self.c_stats["s02_tr"]["move_modifiers"]={"open":1, "rail":99, "h":99, "l":99, "f":2}
        self.c_stats["s02_tr"]["max_group_size"]=10
        self.c_stats["s02_tr"]["base_force_per"]=3
        self.c_stats["s02_tr"]["sprite"]=gallery.content["trn"]["s01"]
        self.c_stats["s02_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,5), "close":(0,0), "ranged":(0,0)}
        self.c_stats["s02_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,10), "close":(-10,-5), "ranged":(0,0) }
        self.c_stats["s02_tr"]["spawn"]="na"
        self.c_stats["s02_tr"]["type"]="unit"

        self.c_stats["m01_tr"]={}
        self.c_stats["m01_tr"]["name"]="Raider"
        self.c_stats["m01_tr"]["max_move"]=4
        self.c_stats["m01_tr"]["max_range"]=1
        self.c_stats["m01_tr"]["move_modifiers"]={"open":1, "rail":99, "h":99, "l":99, "f":3}
        self.c_stats["m01_tr"]["max_group_size"]=3
        self.c_stats["m01_tr"]["base_force_per"]=10
        self.c_stats["m01_tr"]["sprite"]=gallery.content["trn"]["m01"]
        self.c_stats["m01_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(-30,-15), "close":(0,10), "ranged":(0,0) }
        self.c_stats["m01_tr"]["defense_modifiers"]={"open":(-5,0), "h":(-5,0), "l":(0,0), "f":(-30,-20), "close":(0,0), "ranged":(-10,-5) }
        self.c_stats["m01_tr"]["spawn"]="na"
        self.c_stats["m01_tr"]["type"]="unit"


        self.c_stats["s01_vu"]={}
        self.c_stats["s01_vu"]["name"]="Soldier"
        self.c_stats["s01_vu"]["max_move"]=3
        self.c_stats["s01_vu"]["max_range"]=1
        self.c_stats["s01_vu"]["move_modifiers"]={"open":1, "rail":99, "h":99, "l":99, "f":2}
        self.c_stats["s01_vu"]["max_group_size"]=15
        self.c_stats["s01_vu"]["base_force_per"]=2
        self.c_stats["s01_vu"]["sprite"]=gallery.content["trn"]["s01_vu"]
        self.c_stats["s01_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(-5,5), "close":(0,0), "ranged":(0,0)}
        self.c_stats["s01_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,10), "close":(0,0), "ranged":(0,0) }
        self.c_stats["s01_vu"]["spawn"]="na"
        self.c_stats["s01_vu"]["type"]="unit"


        self.c_stats["s02_vu"]={}
        self.c_stats["s02_vu"]["name"]="Ranger"
        self.c_stats["s02_vu"]["max_move"]=2
        self.c_stats["s02_vu"]["max_range"]=4
        self.c_stats["s02_vu"]["move_modifiers"]={"open":1, "rail":99, "h":99, "l":99, "f":2}
        self.c_stats["s02_vu"]["max_group_size"]=10
        self.c_stats["s02_vu"]["base_force_per"]=3
        self.c_stats["s02_vu"]["sprite"]=gallery.content["trn"]["s01_vu"]
        self.c_stats["s02_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,5), "close":(0,0), "ranged":(0,0)}
        self.c_stats["s02_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,10), "close":(-10,-5), "ranged":(0,0) }
        self.c_stats["s02_vu"]["spawn"]="na"
        self.c_stats["s02_vu"]["type"]="unit"


        self.c_stats["m01_vu"]={}
        self.c_stats["m01_vu"]["name"]="Raider"
        self.c_stats["m01_vu"]["max_move"]=4
        self.c_stats["m01_vu"]["max_range"]=1
        self.c_stats["m01_vu"]["move_modifiers"]={"open":1, "rail":99, "h":99, "l":99, "f":3}
        self.c_stats["m01_vu"]["max_group_size"]=3
        self.c_stats["m01_vu"]["base_force_per"]=10
        self.c_stats["m01_vu"]["sprite"]=gallery.content["trn"]["m01"]
        self.c_stats["m01_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(-30,-15), "close":(0,10), "ranged":(0,0) }
        self.c_stats["m01_vu"]["defense_modifiers"]={"open":(-5,0), "h":(-5,0), "l":(0,0), "f":(-30,-20), "close":(0,0), "ranged":(-10,-5) }
        self.c_stats["m01_vu"]["spawn"]="na"
        self.c_stats["m01_vu"]["type"]="unit"


        self.c_stats["Merchandise_tr"]={}
        self.c_stats["Merchandise_tr"]["name"]="Merchandise"
        self.c_stats["Merchandise_tr"]["max_move"]=0
        self.c_stats["Merchandise_tr"]["max_range"]=0
        self.c_stats["Merchandise_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Merchandise_tr"]["max_group_size"]=3
        self.c_stats["Merchandise_tr"]["base_force_per"]=10
        self.c_stats["Merchandise_tr"]["sprite"]=gallery.content["trn"]["merchandise_tr"]
        self.c_stats["Merchandise_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Merchandise_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Merchandise_tr"]["spawn"]="na"
        self.c_stats["Merchandise_tr"]["type"]="wagon"

        self.c_stats["XL Merchandise_tr"]={}
        self.c_stats["XL Merchandise_tr"]["name"]="XL Merchandise"
        self.c_stats["XL Merchandise_tr"]["max_move"]=0
        self.c_stats["XL Merchandise_tr"]["max_range"]=0
        self.c_stats["XL Merchandise_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["XL Merchandise_tr"]["max_group_size"]=4
        self.c_stats["XL Merchandise_tr"]["base_force_per"]=10
        self.c_stats["XL Merchandise_tr"]["sprite"]=gallery.content["trn"]["merchandise_tr"]
        self.c_stats["XL Merchandise_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Merchandise_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Merchandise_tr"]["spawn"]="na"
        self.c_stats["XL Merchandise_tr"]["type"]="wagon"

        self.c_stats["Barracks_tr"]={}
        self.c_stats["Barracks_tr"]["name"]="Barracks"
        self.c_stats["Barracks_tr"]["max_move"]=0
        self.c_stats["Barracks_tr"]["max_range"]=0
        self.c_stats["Barracks_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Barracks_tr"]["max_group_size"]=5
        self.c_stats["Barracks_tr"]["base_force_per"]=10
        self.c_stats["Barracks_tr"]["sprite"]=gallery.content["trn"]["barracks_tr"]
        self.c_stats["Barracks_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Barracks_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Barracks_tr"]["spawn"]="s"
        self.c_stats["Barracks_tr"]["type"]="wagon"

        self.c_stats["XL Barracks_tr"]={}
        self.c_stats["XL Barracks_tr"]["name"]="XL Barracks"
        self.c_stats["XL Barracks_tr"]["max_move"]=0
        self.c_stats["XL Barracks_tr"]["max_range"]=0
        self.c_stats["XL Barracks_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["XL Barracks_tr"]["max_group_size"]=6
        self.c_stats["XL Barracks_tr"]["base_force_per"]=10
        self.c_stats["XL Barracks_tr"]["sprite"]=gallery.content["trn"]["barracks_tr"]
        self.c_stats["XL Barracks_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Barracks_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Barracks_tr"]["spawn"]="s"
        self.c_stats["XL Barracks_tr"]["type"]="wagon"

        self.c_stats["Tender_tr"]={}
        self.c_stats["Tender_tr"]["name"]="Tender"
        self.c_stats["Tender_tr"]["max_move"]=0
        self.c_stats["Tender_tr"]["max_range"]=0
        self.c_stats["Tender_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Tender_tr"]["max_group_size"]=4
        self.c_stats["Tender_tr"]["base_force_per"]=10
        self.c_stats["Tender_tr"]["sprite"]=gallery.content["trn"]["tender_tr"]
        self.c_stats["Tender_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Tender_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Tender_tr"]["spawn"]="na"
        self.c_stats["Tender_tr"]["type"]="wagon"

        self.c_stats["Cannon_tr"]={}
        self.c_stats["Cannon_tr"]["name"]="Cannon"
        self.c_stats["Cannon_tr"]["max_move"]=0
        self.c_stats["Cannon_tr"]["max_range"]=-15
        self.c_stats["Cannon_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Cannon_tr"]["max_group_size"]=7
        self.c_stats["Cannon_tr"]["base_force_per"]=10
        self.c_stats["Cannon_tr"]["sprite"]=gallery.content["trn"]["cannon_tr"]
        self.c_stats["Cannon_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Cannon_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Cannon_tr"]["spawn"]="na"
        self.c_stats["Cannon_tr"]["type"]="wagon"

        self.c_stats["Machine gun_tr"]={}
        self.c_stats["Machine gun_tr"]["name"]="Machine gun"
        self.c_stats["Machine gun_tr"]["max_move"]=0
        self.c_stats["Machine gun_tr"]["max_range"]=8
        self.c_stats["Machine gun_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Machine gun_tr"]["max_group_size"]=6
        self.c_stats["Machine gun_tr"]["base_force_per"]=10
        self.c_stats["Machine gun_tr"]["sprite"]=gallery.content["trn"]["machinegun_tr"]
        self.c_stats["Machine gun_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Machine gun_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Machine gun_tr"]["spawn"]="na"
        self.c_stats["Machine gun_tr"]["type"]="wagon"

        self.c_stats["Prison_tr"]={}
        self.c_stats["Prison_tr"]["name"]="Prison"
        self.c_stats["Prison_tr"]["max_move"]=0
        self.c_stats["Prison_tr"]["max_range"]=0
        self.c_stats["Prison_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Prison_tr"]["max_group_size"]=3
        self.c_stats["Prison_tr"]["base_force_per"]=10
        self.c_stats["Prison_tr"]["sprite"]=gallery.content["trn"]["alcatraz_tr"]
        self.c_stats["Prison_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Prison_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Prison_tr"]["spawn"]="na"
        self.c_stats["Prison_tr"]["type"]="wagon"

        self.c_stats["Alcatraz_tr"]={}
        self.c_stats["Alcatraz_tr"]["name"]="Alcatraz"
        self.c_stats["Alcatraz_tr"]["max_move"]=0
        self.c_stats["Alcatraz_tr"]["max_range"]=0
        self.c_stats["Alcatraz_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Alcatraz_tr"]["max_group_size"]=4
        self.c_stats["Alcatraz_tr"]["base_force_per"]=10
        self.c_stats["Alcatraz_tr"]["sprite"]=gallery.content["trn"]["alcatraz_tr"]
        self.c_stats["Alcatraz_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Alcatraz_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Alcatraz_tr"]["spawn"]="na"
        self.c_stats["Alcatraz_tr"]["type"]="wagon"

        self.c_stats["Livestock_tr"]={}
        self.c_stats["Livestock_tr"]["name"]="Livestock"
        self.c_stats["Livestock_tr"]["max_move"]=0
        self.c_stats["Livestock_tr"]["max_range"]=0
        self.c_stats["Livestock_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Livestock_tr"]["max_group_size"]=4
        self.c_stats["Livestock_tr"]["base_force_per"]=10
        self.c_stats["Livestock_tr"]["sprite"]=gallery.content["trn"]["livestock_tr"]
        self.c_stats["Livestock_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Livestock_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Livestock_tr"]["spawn"]="m"
        self.c_stats["Livestock_tr"]["type"]="wagon"

        self.c_stats["Harpoon_tr"]={}
        self.c_stats["Harpoon_tr"]["name"]="Harpoon"
        self.c_stats["Harpoon_tr"]["max_move"]=0
        self.c_stats["Harpoon_tr"]["max_range"]=0
        self.c_stats["Harpoon_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Harpoon_tr"]["max_group_size"]=3
        self.c_stats["Harpoon_tr"]["base_force_per"]=10
        self.c_stats["Harpoon_tr"]["sprite"]=gallery.content["trn"]["crane_tr"]
        self.c_stats["Harpoon_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Harpoon_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Harpoon_tr"]["spawn"]="na"
        self.c_stats["Harpoon_tr"]["type"]="wagon"

        self.c_stats["Refrigerator_tr"]={}
        self.c_stats["Refrigerator_tr"]["name"]="Refrigerator"
        self.c_stats["Refrigerator_tr"]["max_move"]=0
        self.c_stats["Refrigerator_tr"]["max_range"]=0
        self.c_stats["Refrigerator_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Refrigerator_tr"]["max_group_size"]=3
        self.c_stats["Refrigerator_tr"]["base_force_per"]=10
        self.c_stats["Refrigerator_tr"]["sprite"]=gallery.content["trn"]["merchandise_tr"]
        self.c_stats["Refrigerator_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Refrigerator_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Refrigerator_tr"]["spawn"]="na"
        self.c_stats["Refrigerator_tr"]["type"]="wagon"

        self.c_stats["Bio-greenhouse_tr"]={}
        self.c_stats["Bio-greenhouse_tr"]["name"]="Bio-greenhouse"
        self.c_stats["Bio-greenhouse_tr"]["max_move"]=0
        self.c_stats["Bio-greenhouse_tr"]["max_range"]=0
        self.c_stats["Bio-greenhouse_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Bio-greenhouse_tr"]["max_group_size"]=2
        self.c_stats["Bio-greenhouse_tr"]["base_force_per"]=10
        self.c_stats["Bio-greenhouse_tr"]["sprite"]=gallery.content["trn"]["greenhouse_tr"]
        self.c_stats["Bio-greenhouse_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Bio-greenhouse_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Bio-greenhouse_tr"]["spawn"]="na"
        self.c_stats["Bio-greenhouse_tr"]["type"]="wagon"

        self.c_stats["Tanker_tr"]={}
        self.c_stats["Tanker_tr"]["name"]="Tanker"
        self.c_stats["Tanker_tr"]["max_move"]=0
        self.c_stats["Tanker_tr"]["max_range"]=0
        self.c_stats["Tanker_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Tanker_tr"]["max_group_size"]=2
        self.c_stats["Tanker_tr"]["base_force_per"]=10
        self.c_stats["Tanker_tr"]["sprite"]=gallery.content["trn"]["tanker_tr"]
        self.c_stats["Tanker_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Tanker_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Tanker_tr"]["spawn"]="na"
        self.c_stats["Tanker_tr"]["type"]="wagon"

        self.c_stats["XL Tanker_tr"]={}
        self.c_stats["XL Tanker_tr"]["name"]="Tanker"
        self.c_stats["XL Tanker_tr"]["max_move"]=0
        self.c_stats["XL Tanker_tr"]["max_range"]=0
        self.c_stats["XL Tanker_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["XL Tanker_tr"]["max_group_size"]=2
        self.c_stats["XL Tanker_tr"]["base_force_per"]=10
        self.c_stats["XL Tanker_tr"]["sprite"]=gallery.content["trn"]["tanker_tr"]
        self.c_stats["XL Tanker_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Tanker_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Tanker_tr"]["spawn"]="na"
        self.c_stats["XL Tanker_tr"]["type"]="wagon"

        self.c_stats["Observation box_tr"]={}
        self.c_stats["Observation box_tr"]["name"]="Observation box"
        self.c_stats["Observation box_tr"]["max_move"]=0
        self.c_stats["Observation box_tr"]["max_range"]=0
        self.c_stats["Observation box_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Observation box_tr"]["max_group_size"]=3
        self.c_stats["Observation box_tr"]["base_force_per"]=10
        self.c_stats["Observation box_tr"]["sprite"]=gallery.content["trn"]["observatory_tr"]
        self.c_stats["Observation box_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Observation box_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Observation box_tr"]["spawn"]="na"
        self.c_stats["Observation box_tr"]["type"]="wagon"

        self.c_stats["Observatory_tr"]={}
        self.c_stats["Observatory_tr"]["name"]="Observatory"
        self.c_stats["Observatory_tr"]["max_move"]=0
        self.c_stats["Observatory_tr"]["max_range"]=0
        self.c_stats["Observatory_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Observatory_tr"]["max_group_size"]=3
        self.c_stats["Observatory_tr"]["base_force_per"]=10
        self.c_stats["Observatory_tr"]["sprite"]=gallery.content["trn"]["observatory_tr"]
        self.c_stats["Observatory_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Observatory_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Observatory_tr"]["spawn"]="na"
        self.c_stats["Observatory_tr"]["type"]="wagon"

        self.c_stats["Spy_tr"]={}
        self.c_stats["Spy_tr"]["name"]="Spy"
        self.c_stats["Spy_tr"]["max_move"]=0
        self.c_stats["Spy_tr"]["max_range"]=0
        self.c_stats["Spy_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Spy_tr"]["max_group_size"]=4
        self.c_stats["Spy_tr"]["base_force_per"]=10
        self.c_stats["Spy_tr"]["sprite"]=gallery.content["trn"]["spy_tr"]
        self.c_stats["Spy_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Spy_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Spy_tr"]["spawn"]="na"
        self.c_stats["Spy_tr"]["type"]="wagon"

        #self.c_stats["Missile launcher_tr"]={}
        #self.c_stats["Missile launcher_tr"]["name"]="Missile launcher"
        #self.c_stats["Missile launcher_tr"]["max_move"]=0
        #self.c_stats["Missile launcher_tr"]["max_range"]=0
        #self.c_stats["Missile launcher_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        #self.c_stats["Missile launcher_tr"]["max_group_size"]=4
        #self.c_stats["Missile launcher_tr"]["base_force_per"]=10
        #self.c_stats["Missile launcher_tr"]["sprite"]=gallery.content["trn"]["missile_launcher_tr"]
        #self.c_stats["Missile launcher_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        #self.c_stats["Missile launcher_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        #self.c_stats["Missile launcher_tr"]["spawn"]="na"
        #self.c_stats["Missile launcher_tr"]["type"]="wagon"

        self.c_stats["Boiler_tr"]={}
        self.c_stats["Boiler_tr"]["name"]="Boiler"
        self.c_stats["Boiler_tr"]["max_move"]=0
        self.c_stats["Boiler_tr"]["max_range"]=0
        self.c_stats["Boiler_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Boiler_tr"]["max_group_size"]=5
        self.c_stats["Boiler_tr"]["base_force_per"]=10
        self.c_stats["Boiler_tr"]["sprite"]=gallery.content["trn"]["boiler_tr"]
        self.c_stats["Boiler_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Boiler_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Boiler_tr"]["spawn"]="na"
        self.c_stats["Boiler_tr"]["type"]="wagon"

        self.c_stats["Crane_tr"]={}
        self.c_stats["Crane_tr"]["name"]="Crane"
        self.c_stats["Crane_tr"]["max_move"]=0
        self.c_stats["Crane_tr"]["max_range"]=0
        self.c_stats["Crane_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Crane_tr"]["max_group_size"]=3
        self.c_stats["Crane_tr"]["base_force_per"]=10
        self.c_stats["Crane_tr"]["sprite"]=gallery.content["trn"]["crane_tr"]
        self.c_stats["Crane_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Crane_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Crane_tr"]["spawn"]="na"
        self.c_stats["Crane_tr"]["type"]="wagon"

        self.c_stats["Drill_tr"]={}
        self.c_stats["Drill_tr"]["name"]="Drill"
        self.c_stats["Drill_tr"]["max_move"]=0
        self.c_stats["Drill_tr"]["max_range"]=0
        self.c_stats["Drill_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Drill_tr"]["max_group_size"]=6
        self.c_stats["Drill_tr"]["base_force_per"]=10
        self.c_stats["Drill_tr"]["sprite"]=gallery.content["trn"]["drill_tr"]
        self.c_stats["Drill_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Drill_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Drill_tr"]["spawn"]="na"
        self.c_stats["Drill_tr"]["type"]="wagon"

        self.c_stats["Locomotive_tr"]={}
        self.c_stats["Locomotive_tr"]["name"]="Locomotive"
        self.c_stats["Locomotive_tr"]["max_move"]=4
        self.c_stats["Locomotive_tr"]["max_range"]=0
        self.c_stats["Locomotive_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Locomotive_tr"]["max_group_size"]=8
        self.c_stats["Locomotive_tr"]["base_force_per"]=10
        self.c_stats["Locomotive_tr"]["sprite"]=gallery.content["trn"]["locomotive_tr"]
        self.c_stats["Locomotive_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Locomotive_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Locomotive_tr"]["spawn"]="na"
        self.c_stats["Locomotive_tr"]["type"]="wagon"

        self.c_stats["Command and Control_tr"]={}
        self.c_stats["Command and Control_tr"]["name"]="Command and Control"
        self.c_stats["Command and Control_tr"]["max_move"]=0
        self.c_stats["Command and Control_tr"]["max_range"]=0
        self.c_stats["Command and Control_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Command and Control_tr"]["max_group_size"]=5
        self.c_stats["Command and Control_tr"]["base_force_per"]=10
        self.c_stats["Command and Control_tr"]["sprite"]=gallery.content["trn"]["command_control_tr"]
        self.c_stats["Command and Control_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Command and Control_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Command and Control_tr"]["spawn"]="na"
        self.c_stats["Command and Control_tr"]["type"]="wagon"

        self.c_stats["Quarters_tr"]={}
        self.c_stats["Quarters_tr"]["name"]="Quarters"
        self.c_stats["Quarters_tr"]["max_move"]=0
        self.c_stats["Quarters_tr"]["max_range"]=0
        self.c_stats["Quarters_tr"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Quarters_tr"]["max_group_size"]=5
        self.c_stats["Quarters_tr"]["base_force_per"]=10
        self.c_stats["Quarters_tr"]["sprite"]=gallery.content["trn"]["quarters_tr"]
        self.c_stats["Quarters_tr"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Quarters_tr"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Quarters_tr"]["spawn"]="na"
        self.c_stats["Quarters_tr"]["type"]="wagon"

        self.c_stats["Merchandise_vu"]={}
        self.c_stats["Merchandise_vu"]["name"]="Merchandise"
        self.c_stats["Merchandise_vu"]["max_move"]=0
        self.c_stats["Merchandise_vu"]["max_range"]=0
        self.c_stats["Merchandise_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Merchandise_vu"]["max_group_size"]=3
        self.c_stats["Merchandise_vu"]["base_force_per"]=10
        self.c_stats["Merchandise_vu"]["sprite"]=gallery.content["trn"]["merchandise_vu"]
        self.c_stats["Merchandise_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Merchandise_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Merchandise_vu"]["spawn"]="na"
        self.c_stats["Merchandise_vu"]["type"]="wagon"

        self.c_stats["XL Merchandise_vu"]={}
        self.c_stats["XL Merchandise_vu"]["name"]="XL Merchandise"
        self.c_stats["XL Merchandise_vu"]["max_move"]=0
        self.c_stats["XL Merchandise_vu"]["max_range"]=0
        self.c_stats["XL Merchandise_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["XL Merchandise_vu"]["max_group_size"]=4
        self.c_stats["XL Merchandise_vu"]["base_force_per"]=10
        self.c_stats["XL Merchandise_vu"]["sprite"]=gallery.content["trn"]["merchandise_vu"]
        self.c_stats["XL Merchandise_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Merchandise_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Merchandise_vu"]["spawn"]="na"
        self.c_stats["XL Merchandise_vu"]["type"]="wagon"

        self.c_stats["Barracks_vu"]={}
        self.c_stats["Barracks_vu"]["name"]="Barracks"
        self.c_stats["Barracks_vu"]["max_move"]=0
        self.c_stats["Barracks_vu"]["max_range"]=0
        self.c_stats["Barracks_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Barracks_vu"]["max_group_size"]=5
        self.c_stats["Barracks_vu"]["base_force_per"]=10
        self.c_stats["Barracks_vu"]["sprite"]=gallery.content["trn"]["barracks_vu"]
        self.c_stats["Barracks_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Barracks_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Barracks_vu"]["spawn"]="s"
        self.c_stats["Barracks_vu"]["type"]="wagon"

        self.c_stats["XL Barracks_vu"]={}
        self.c_stats["XL Barracks_vu"]["name"]="XL Barracks"
        self.c_stats["XL Barracks_vu"]["max_move"]=0
        self.c_stats["XL Barracks_vu"]["max_range"]=0
        self.c_stats["XL Barracks_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["XL Barracks_vu"]["max_group_size"]=6
        self.c_stats["XL Barracks_vu"]["base_force_per"]=10
        self.c_stats["XL Barracks_vu"]["sprite"]=gallery.content["trn"]["barracks_vu"]
        self.c_stats["XL Barracks_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Barracks_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Barracks_vu"]["spawn"]="s"
        self.c_stats["XL Barracks_vu"]["type"]="wagon"

        self.c_stats["Tender_vu"]={}
        self.c_stats["Tender_vu"]["name"]="Tender"
        self.c_stats["Tender_vu"]["max_move"]=0
        self.c_stats["Tender_vu"]["max_range"]=0
        self.c_stats["Tender_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Tender_vu"]["max_group_size"]=4
        self.c_stats["Tender_vu"]["base_force_per"]=10
        self.c_stats["Tender_vu"]["sprite"]=gallery.content["trn"]["tender_vu"]
        self.c_stats["Tender_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Tender_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Tender_vu"]["spawn"]="na"
        self.c_stats["Tender_vu"]["type"]="wagon"

        self.c_stats["Cannon_vu"]={}
        self.c_stats["Cannon_vu"]["name"]="Cannon"
        self.c_stats["Cannon_vu"]["max_move"]=0
        self.c_stats["Cannon_vu"]["max_range"]=-15
        self.c_stats["Cannon_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Cannon_vu"]["max_group_size"]=7
        self.c_stats["Cannon_vu"]["base_force_per"]=10
        self.c_stats["Cannon_vu"]["sprite"]=gallery.content["trn"]["cannon_vu"]
        self.c_stats["Cannon_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Cannon_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Cannon_vu"]["spawn"]="na"
        self.c_stats["Cannon_vu"]["type"]="wagon"

        self.c_stats["Machine gun_vu"]={}
        self.c_stats["Machine gun_vu"]["name"]="Machine gun"
        self.c_stats["Machine gun_vu"]["max_move"]=0
        self.c_stats["Machine gun_vu"]["max_range"]=8
        self.c_stats["Machine gun_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Machine gun_vu"]["max_group_size"]=6
        self.c_stats["Machine gun_vu"]["base_force_per"]=10
        self.c_stats["Machine gun_vu"]["sprite"]=gallery.content["trn"]["machinegun_vu"]
        self.c_stats["Machine gun_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Machine gun_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Machine gun_vu"]["spawn"]="na"
        self.c_stats["Machine gun_vu"]["type"]="wagon"

        self.c_stats["Prison_vu"]={}
        self.c_stats["Prison_vu"]["name"]="Prison"
        self.c_stats["Prison_vu"]["max_move"]=0
        self.c_stats["Prison_vu"]["max_range"]=0
        self.c_stats["Prison_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Prison_vu"]["max_group_size"]=3
        self.c_stats["Prison_vu"]["base_force_per"]=10
        self.c_stats["Prison_vu"]["sprite"]=gallery.content["trn"]["alcatraz_vu"]
        self.c_stats["Prison_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Prison_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Prison_vu"]["spawn"]="na"
        self.c_stats["Prison_vu"]["type"]="wagon"

        self.c_stats["Alcatraz_vu"]={}
        self.c_stats["Alcatraz_vu"]["name"]="Alcatraz"
        self.c_stats["Alcatraz_vu"]["max_move"]=0
        self.c_stats["Alcatraz_vu"]["max_range"]=0
        self.c_stats["Alcatraz_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Alcatraz_vu"]["max_group_size"]=4
        self.c_stats["Alcatraz_vu"]["base_force_per"]=10
        self.c_stats["Alcatraz_vu"]["sprite"]=gallery.content["trn"]["alcatraz_vu"]
        self.c_stats["Alcatraz_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Alcatraz_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Alcatraz_vu"]["spawn"]="na"
        self.c_stats["Alcatraz_vu"]["type"]="wagon"

        self.c_stats["Livestock_vu"]={}
        self.c_stats["Livestock_vu"]["name"]="Livestock"
        self.c_stats["Livestock_vu"]["max_move"]=0
        self.c_stats["Livestock_vu"]["max_range"]=0
        self.c_stats["Livestock_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Livestock_vu"]["max_group_size"]=4
        self.c_stats["Livestock_vu"]["base_force_per"]=10
        self.c_stats["Livestock_vu"]["sprite"]=gallery.content["trn"]["livestock_vu"]
        self.c_stats["Livestock_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Livestock_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Livestock_vu"]["spawn"]="m"
        self.c_stats["Livestock_vu"]["type"]="wagon"

        self.c_stats["Harpoon_vu"]={}
        self.c_stats["Harpoon_vu"]["name"]="Harpoon"
        self.c_stats["Harpoon_vu"]["max_move"]=0
        self.c_stats["Harpoon_vu"]["max_range"]=0
        self.c_stats["Harpoon_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Harpoon_vu"]["max_group_size"]=3
        self.c_stats["Harpoon_vu"]["base_force_per"]=10
        self.c_stats["Harpoon_vu"]["sprite"]=gallery.content["trn"]["crane_vu"]
        self.c_stats["Harpoon_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Harpoon_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Harpoon_vu"]["spawn"]="na"
        self.c_stats["Harpoon_vu"]["type"]="wagon"

        self.c_stats["Refrigerator_vu"]={}
        self.c_stats["Refrigerator_vu"]["name"]="Refrigerator"
        self.c_stats["Refrigerator_vu"]["max_move"]=0
        self.c_stats["Refrigerator_vu"]["max_range"]=0
        self.c_stats["Refrigerator_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Refrigerator_vu"]["max_group_size"]=3
        self.c_stats["Refrigerator_vu"]["base_force_per"]=10
        self.c_stats["Refrigerator_vu"]["sprite"]=gallery.content["trn"]["merchandise_vu"]
        self.c_stats["Refrigerator_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Refrigerator_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Refrigerator_vu"]["spawn"]="na"
        self.c_stats["Refrigerator_vu"]["type"]="wagon"

        self.c_stats["Bio-greenhouse_vu"]={}
        self.c_stats["Bio-greenhouse_vu"]["name"]="Bio-greenhouse"
        self.c_stats["Bio-greenhouse_vu"]["max_move"]=0
        self.c_stats["Bio-greenhouse_vu"]["max_range"]=0
        self.c_stats["Bio-greenhouse_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Bio-greenhouse_vu"]["max_group_size"]=2
        self.c_stats["Bio-greenhouse_vu"]["base_force_per"]=10
        self.c_stats["Bio-greenhouse_vu"]["sprite"]=gallery.content["trn"]["greenhouse_vu"]
        self.c_stats["Bio-greenhouse_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Bio-greenhouse_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Bio-greenhouse_vu"]["spawn"]="na"
        self.c_stats["Bio-greenhouse_vu"]["type"]="wagon"

        self.c_stats["Tanker_vu"]={}
        self.c_stats["Tanker_vu"]["name"]="Tanker"
        self.c_stats["Tanker_vu"]["max_move"]=0
        self.c_stats["Tanker_vu"]["max_range"]=0
        self.c_stats["Tanker_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Tanker_vu"]["max_group_size"]=2
        self.c_stats["Tanker_vu"]["base_force_per"]=10
        self.c_stats["Tanker_vu"]["sprite"]=gallery.content["trn"]["tanker_vu"]
        self.c_stats["Tanker_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Tanker_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Tanker_vu"]["spawn"]="na"
        self.c_stats["Tanker_vu"]["type"]="wagon"

        self.c_stats["XL Tanker_vu"]={}
        self.c_stats["XL Tanker_vu"]["name"]="Tanker"
        self.c_stats["XL Tanker_vu"]["max_move"]=0
        self.c_stats["XL Tanker_vu"]["max_range"]=0
        self.c_stats["XL Tanker_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["XL Tanker_vu"]["max_group_size"]=2
        self.c_stats["XL Tanker_vu"]["base_force_per"]=10
        self.c_stats["XL Tanker_vu"]["sprite"]=gallery.content["trn"]["tanker_vu"]
        self.c_stats["XL Tanker_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Tanker_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["XL Tanker_vu"]["spawn"]="na"
        self.c_stats["XL Tanker_vu"]["type"]="wagon"

        self.c_stats["Observation box_vu"]={}
        self.c_stats["Observation box_vu"]["name"]="Observation box"
        self.c_stats["Observation box_vu"]["max_move"]=0
        self.c_stats["Observation box_vu"]["max_range"]=0
        self.c_stats["Observation box_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Observation box_vu"]["max_group_size"]=3
        self.c_stats["Observation box_vu"]["base_force_per"]=10
        self.c_stats["Observation box_vu"]["sprite"]=gallery.content["trn"]["observatory_vu"]
        self.c_stats["Observation box_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Observation box_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Observation box_vu"]["spawn"]="na"
        self.c_stats["Observation box_vu"]["type"]="wagon"

        self.c_stats["Observatory_vu"]={}
        self.c_stats["Observatory_vu"]["name"]="Observatory"
        self.c_stats["Observatory_vu"]["max_move"]=0
        self.c_stats["Observatory_vu"]["max_range"]=0
        self.c_stats["Observatory_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Observatory_vu"]["max_group_size"]=3
        self.c_stats["Observatory_vu"]["base_force_per"]=10
        self.c_stats["Observatory_vu"]["sprite"]=gallery.content["trn"]["observatory_vu"]
        self.c_stats["Observatory_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Observatory_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Observatory_vu"]["spawn"]="na"
        self.c_stats["Observatory_vu"]["type"]="wagon"

        self.c_stats["Spy_vu"]={}
        self.c_stats["Spy_vu"]["name"]="Spy"
        self.c_stats["Spy_vu"]["max_move"]=0
        self.c_stats["Spy_vu"]["max_range"]=0
        self.c_stats["Spy_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Spy_vu"]["max_group_size"]=4
        self.c_stats["Spy_vu"]["base_force_per"]=10
        self.c_stats["Spy_vu"]["sprite"]=gallery.content["trn"]["spy_vu"]
        self.c_stats["Spy_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Spy_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Spy_vu"]["spawn"]="na"
        self.c_stats["Spy_vu"]["type"]="wagon"

        #self.c_stats["Missile launcher_vu"]={}
        #self.c_stats["Missile launcher_vu"]["name"]="Missile launcher"
        #self.c_stats["Missile launcher_vu"]["max_move"]=0
        #self.c_stats["Missile launcher_vu"]["max_range"]=0
        #self.c_stats["Missile launcher_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        #self.c_stats["Missile launcher_vu"]["max_group_size"]=4
        #self.c_stats["Missile launcher_vu"]["base_force_per"]=10
        #self.c_stats["Missile launcher_vu"]["sprite"]=gallery.content["trn"]["missile_launcher_vu"]
        #self.c_stats["Missile launcher_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        #self.c_stats["Missile launcher_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        #self.c_stats["Missile launcher_vu"]["spawn"]="na"
        #self.c_stats["Missile launcher_vu"]["type"]="wagon"

        self.c_stats["Boiler_vu"]={}
        self.c_stats["Boiler_vu"]["name"]="Boiler"
        self.c_stats["Boiler_vu"]["max_move"]=0
        self.c_stats["Boiler_vu"]["max_range"]=0
        self.c_stats["Boiler_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Boiler_vu"]["max_group_size"]=5
        self.c_stats["Boiler_vu"]["base_force_per"]=10
        self.c_stats["Boiler_vu"]["sprite"]=gallery.content["trn"]["boiler_vu"]
        self.c_stats["Boiler_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Boiler_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Boiler_vu"]["spawn"]="na"
        self.c_stats["Boiler_vu"]["type"]="wagon"

        self.c_stats["Crane_vu"]={}
        self.c_stats["Crane_vu"]["name"]="Crane"
        self.c_stats["Crane_vu"]["max_move"]=0
        self.c_stats["Crane_vu"]["max_range"]=0
        self.c_stats["Crane_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Crane_vu"]["max_group_size"]=3
        self.c_stats["Crane_vu"]["base_force_per"]=10
        self.c_stats["Crane_vu"]["sprite"]=gallery.content["trn"]["crane_vu"]
        self.c_stats["Crane_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Crane_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Crane_vu"]["spawn"]="na"
        self.c_stats["Crane_vu"]["type"]="wagon"

        self.c_stats["Drill_vu"]={}
        self.c_stats["Drill_vu"]["name"]="Drill"
        self.c_stats["Drill_vu"]["max_move"]=0
        self.c_stats["Drill_vu"]["max_range"]=0
        self.c_stats["Drill_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Drill_vu"]["max_group_size"]=6
        self.c_stats["Drill_vu"]["base_force_per"]=10
        self.c_stats["Drill_vu"]["sprite"]=gallery.content["trn"]["drill_vu"]
        self.c_stats["Drill_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Drill_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Drill_vu"]["spawn"]="na"
        self.c_stats["Drill_vu"]["type"]="wagon"

        self.c_stats["Locomotive_vu"]={}
        self.c_stats["Locomotive_vu"]["name"]="Locomotive"
        self.c_stats["Locomotive_vu"]["max_move"]=4
        self.c_stats["Locomotive_vu"]["max_range"]=0
        self.c_stats["Locomotive_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Locomotive_vu"]["max_group_size"]=8
        self.c_stats["Locomotive_vu"]["base_force_per"]=10
        self.c_stats["Locomotive_vu"]["sprite"]=gallery.content["trn"]["locomotive_vu"]
        self.c_stats["Locomotive_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Locomotive_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Locomotive_vu"]["spawn"]="na"
        self.c_stats["Locomotive_vu"]["type"]="wagon"

        self.c_stats["Command and Control_vu"]={}
        self.c_stats["Command and Control_vu"]["name"]="Command and Control"
        self.c_stats["Command and Control_vu"]["max_move"]=0
        self.c_stats["Command and Control_vu"]["max_range"]=0
        self.c_stats["Command and Control_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        self.c_stats["Command and Control_vu"]["max_group_size"]=5
        self.c_stats["Command and Control_vu"]["base_force_per"]=10
        self.c_stats["Command and Control_vu"]["sprite"]=gallery.content["trn"]["command_control_vu"]
        self.c_stats["Command and Control_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Command and Control_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        self.c_stats["Command and Control_vu"]["spawn"]="na"
        self.c_stats["Command and Control_vu"]["type"]="wagon"

        #self.c_stats["Quarters_vu"]={}
        #self.c_stats["Quarters_vu"]["name"]="Quarters"
        #self.c_stats["Quarters_vu"]["max_move"]=0
        #self.c_stats["Quarters_vu"]["max_range"]=0
        #self.c_stats["Quarters_vu"]["move_modifiers"] ={"open":99, "rail":1, "h":99, "l":99, "f":99}
        #self.c_stats["Quarters_vu"]["max_group_size"]=5
        #self.c_stats["Quarters_vu"]["base_force_per"]=10
        #self.c_stats["Quarters_vu"]["sprite"]=gallery.content["trn"]["quarters_vu"]
        #self.c_stats["Quarters_vu"]["attack_modifiers"] ={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        #self.c_stats["Quarters_vu"]["defense_modifiers"]={"open":(0,0), "h":(0,0), "l":(0,0), "f":(0,0), "close":(0,0), "ranged":(0,0) }
        #self.c_stats["Quarters_vu"]["spawn"]="na"
        #self.c_stats["Quarters_vu"]["type"]="wagon"

        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].top           ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].bottom        ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].left          ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].right         ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].center        ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].origin        ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].topleft       ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].topright      ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].bottomleft    ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].bottomright   ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].midtop        ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].midbottom     ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].midtopleft    ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].midtopright   ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].midbottomleft ))
        #print(str(self.map.get("combat").cells[self.target_tile[0]][self.target_tile[1]].midbottomright))
        #
