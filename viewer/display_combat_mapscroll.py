# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import ScrollingManager
from cocos.sprite import Sprite
from controller import events
from . import ActorCombatant
from . import Gallery
from model import Config
import random
from cocos.rect import Rect
from cocos.text import Label
from .button_gen import ButtonGen
from math import trunc
from cocos.layer import ColorLayer
import time
from collections import OrderedDict 
from cocos.draw import Line
from math import sqrt

class DisplayCombatMapscroll(ScrollingManager):
    map_elements={1 : "h01", 2 : "h02", 3 : "h03", 4 : "f01", 5 : "f02", 6 : "f03", 7 : "l01", 8 : "l02", 9 : "l03"}
    map_groups  ={1 : "h", 2 : "f", 3 : "l"}
    """edge scrollable scrolling manager"""
    def __init__(self, viewport_h):
        self.viewport_height=viewport_h
        viewport=Rect(0,self.viewport_height,director.window.width,director.window.height-self.viewport_height) #director.window
        ScrollingManager.__init__(self, viewport)
        self.config = Config()
        self.gallery = Gallery()
        self.is_event_handler = True
        self.sprite_list = {}
        # scrolling
        self.inscroll=False
        self.scroll_direction = (0,0)
        self.marked_tile=(-1, -1)
        self.combatants = {}
        self.valid_squares = {}
        self.move_path = []
        #self.fire_path = []
        self.spawn_unit="na"
        self.bracket = Sprite(self.gallery.content["trn"]["bracket"])
        self.bracket.image_anchor = 0, 0
        self.bracket.scale = 1
        self.bracket.x = -1000
        self.bracket.y = -1000
        self.bracket_sel = Sprite(self.gallery.content["trn"]["bracket_sel"])
        self.bracket_sel.image_anchor = 0, 0
        self.bracket_sel.scale = 1
        self.bracket_sel.x = -1000
        self.bracket_sel.y = -1000

        self.adjacent_tiles = OrderedDict() 
        self.adjacent_tiles["N"]=( 0,  1)
        self.adjacent_tiles["E"]=( 1,  0)
        self.adjacent_tiles["S"]=( 0, -1)
        self.adjacent_tiles["W"]=(-1,  0)
        self.adjacent_tiles["B"]=( 1,  1) 
        self.adjacent_tiles["C"]=( 1, -1) 
        self.adjacent_tiles["D"]=(-1, -1) 
        self.adjacent_tiles["A"]=(-1,  1)





    def init_tactical_map(self):  
        self.map = self.get("combat")
        #self.map._set_scale(0.66)
        self.base_middle = self.pixel_from_screen(int(director.window.width/2), int((director.window.height+self.viewport_height)/2))
        self.update_properties()
        self.generate_tactical_map()
        self.transarctica_combat_train = ActorCombatant(self,"transarctica_combat_train","_tr")
        self.transarctica_combat_train.image_anchor = 0, -28
        self.vu_combat_train = ActorCombatant(self,"vu_combat_train","_vu")
        self.vu_combat_train.image_anchor = 0, -28
        self.place_trains()
        self.place_combatants(True)
        self.map.add(self.bracket, name="bracket")
        self.map.add(self.bracket_sel, name="bracket_sel")
        self.LOS = Line((0,0),(1,1),(255, 0, 0, 255),2)



    def add_sprite(self, spr, name):
        self.map.add(spr)
        self.sprite_list[name] = spr

    def remove_sprite(self, spr, name):
        self.map.remove(self.sprite_list[name])
        self.sprite_list.pop(name)

    def place_trains(self):  
        cell = self.map.cells

        combat_train=self.transarctica_combat_train
        combat_train.place_train(30,0)
        self.transarctica_combat_train_layout=[]
        self.place_wagon(combat_train,"Cannon")
        self.place_wagon(combat_train,"Merchandise")
        self.place_wagon(combat_train,"Tanker")
        self.place_wagon(combat_train,"Locomotive")
        self.place_wagon(combat_train,"Tender")
        self.place_wagon(combat_train,"Machine gun")
        self.place_wagon(combat_train,"Barracks")
        self.place_wagon(combat_train,"Livestock")
        self.map.add(combat_train)
        self.transarctica_combat_train_layout.reverse()

        combat_train=self.vu_combat_train
        combat_train.place_train(40,len(cell[0])-1)
        self.vu_combat_train_layout=[]
        self.place_wagon(combat_train,"Merchandise")
        self.place_wagon(combat_train,"Merchandise")
        self.place_wagon(combat_train,"Cannon")
        self.place_wagon(combat_train,"Merchandise")
        self.place_wagon(combat_train,"Tanker")
        self.place_wagon(combat_train,"Locomotive")
        self.place_wagon(combat_train,"Tender")
        self.place_wagon(combat_train,"Tender")
        self.place_wagon(combat_train,"Barracks")
        self.place_wagon(combat_train,"Livestock")
        self.place_wagon(combat_train,"Machine gun")
        self.map.add(combat_train)
        self.vu_combat_train_layout.reverse()

    def place_wagon(self,combat_train,wagon):
        cell = self.map.cells
        combat_unit = ActorCombatant(self,wagon,combat_train.side)
        params=combat_train.add_wagon_b(wagon, combat_unit.force)
        combat_unit.wagon_width=params[0]
        combat_unit.wagon_id=params[1]
        if combat_train.side=="_tr":
            ty=0        
        else:
            ty=len(cell[0])-1        

        for tx in range(combat_train.left_tx,combat_train.left_tx+combat_unit.wagon_width,1):
            self.combatants["trn_"+str(tx)+"_"+str(ty)] = combat_unit
            if combat_train.side=="_tr":
                self.transarctica_combat_train_layout.append(combat_unit)
            else:
                self.vu_combat_train_layout.append(combat_unit)

    def generate_tactical_map(self):  
        patching={"f":0, "h":0, "l":0, "open": 0, "rail": 0, "any":0}
        cell = self.map.cells
        for tx, x in enumerate(cell):
            for ty, y in enumerate(x):
                if cell[tx][ty].properties["terrain"]!="rail":
                    if (tx>0) and (tx<len(cell)-1) and (ty>0) and (ty<len(cell[tx])-1):
                        patching["h"]=0
                        patching["f"]=0
                        patching[cell[tx-1][ty-1].properties["terrain"]]+=1
                        patching[cell[tx-0][ty-1].properties["terrain"]]+=1
                        patching[cell[tx-1][ty-0].properties["terrain"]]+=1
                        patching[cell[tx+1][ty-1].properties["terrain"]]+=1
                        if patching["h"]+patching["f"]>0:
                            if (patching["h"]>=patching["f"]):
                                pref_patch="h"
                            else:
                                pref_patch="f"
                        else:
                            pref_patch="any"

                        if random.randint(0, 11)>=10-2*patching[pref_patch]:
                            if pref_patch=="any":
                                grid=self.map_groups[random.randint(1,len(self.map_groups))]
                            else:
                                grid=pref_patch
                            try:
                                cell[tx][ty].properties["terrain"]=grid
                                grid+="0"+str(random.randint(1,3))
                                gridsprite = Sprite(self.gallery.content["trn"][grid], position=(((tx+0.5)*self.map.tw, (ty+0.5)*self.map.tw)))
                                self.map.add(gridsprite, name="trn_"+str(tx)+"_"+str(ty))
                            except:
                                A=1

    def place_combatants(self, randomized):
        if randomized:
            cell = self.map.cells
            for tx, x in enumerate(cell):
                for ty, y in enumerate(x):
                    if cell[tx][ty].properties["terrain"]=="open":
                        if random.randint(0, 1)==0:
                            side="_tr"
                        else:
                            side="_vu"
    
                        if random.randint(0, 70)==2:
                            combat_unit = ActorCombatant(self,"s01",side)
                        elif random.randint(0, 70)==2:
                            combat_unit = ActorCombatant(self,"s02",side)
                        elif random.randint(0, 140)==2:
                            combat_unit = ActorCombatant(self,"m01",side)
                        else:
                            combat_unit = None

                        if combat_unit != None:
                            combat_unit.scale = 0.9
                            combat_unit.x=(tx+0.5)*self.map.tw
                            combat_unit.y=(ty+0.5)*self.map.tw
                            combat_unit.image=combat_unit.stat["sprite"]
                            self.map.add(combat_unit, name="trn_"+str(tx)+"_"+str(ty))
                            self.combatants["trn_"+str(tx)+"_"+str(ty)] = combat_unit


    def on_mouse_motion(self, x, y, dx, dy):
        tw=self.map.tw
        cx, cy = director.get_virtual_coordinates(x, y)
        cell=self.map.cells
        tx = int((cx + self.map.view_x) / tw)
        ty = int((cy + self.map.view_y-self.viewport_height) / tw)

        if (x < tw/2) and (x > 0): 
            step_x = -tw
        elif (x > director.window.width-tw/2) and (x < director.window.width) : 
            step_x = tw
        else:
            step_x = 0
        
        if step_x != 0 :
            self.scroll_direction = (step_x, 0)
            self.schedule(self.scroll)
        else:
            self.scroll_direction = (0,0)
            self.unschedule(self.scroll)
        if (self.marked_tile[0]>=0): 
            if ("trn_"+str(tx)+"_"+str(ty) in self.valid_squares): 
                if self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="move":
                    self.bracket.image=self.gallery.content["trn"]["bracket"]
                elif self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="melee":
                    self.bracket.image=self.gallery.content["trn"]["advance"]
                elif self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="ranged":
                    self.bracket.image=self.gallery.content["trn"]["crosshair"]
                elif self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="indirect":
                    self.bracket.image=self.gallery.content["trn"]["crosshair"]                    
                else:
                    self.bracket.image=self.gallery.content["trn"]["bracket"]
            else:
                self.bracket.image=self.gallery.content["trn"]["bracket"]

        self.bracket.x=tx*tw
        self.bracket.y=ty*tw

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        tw=self.map.tw
        cx, cy = director.get_virtual_coordinates(x, y)
        cell=self.map.cells
        tx = int((cx + self.map.view_x) / tw)
        ty = int((cy + self.map.view_y-self.viewport_height) / tw)
        if (tx < 0) or (ty < 0) or (tx >= len(cell)) or (ty >= len(cell[tx])):
            return  # click outside map

        if (self.marked_tile[0]<0) and (self.marked_tile!=(tx,ty)):
            if ("trn_"+str(tx)+"_"+str(ty) in self.valid_squares): 
                if self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="move":
                    if self.spawn_unit!="na":
                        combat_unit = []
                        combat_unit.append(ActorCombatant(self,"s01","_tr"))
                        combat_unit.append(ActorCombatant(self,"s02","_tr"))
                        combat_unit.append(ActorCombatant(self,"m01","_tr"))
                        
                        if combat_unit != None:
                            combat_unit.scale = 0.9
                            combat_unit.x=(tx+0.5)*self.map.tw
                            combat_unit.y=(ty+0.5)*self.map.tw
                            combat_unit.image=combat_unit.stat["sprite"]
                            self.map.add(combat_unit, name="trn_"+str(tx)+"_"+str(ty))
                            self.combatants["trn_"+str(tx)+"_"+str(ty)] = combat_unit

#                                    self.spawn_unit="na"

        print(str((scroll_x, scroll_y)))

    def on_mouse_press(self, x, y, buttons, modifiers):
        """event handler"""
        tw=self.map.tw
        cx, cy = director.get_virtual_coordinates(x, y)
        cell=self.map.cells
        tx = int((cx + self.map.view_x) / tw)
        ty = int((cy + self.map.view_y-self.viewport_height) / tw)
        if (tx < 0) or (ty < 0) or (tx >= len(cell)) or (ty >= len(cell[tx])):
            return  # click outside map
        else:
            if buttons == 1:  # 1: left, 2: middle etc.
                if self.marked_tile[0]<0:
                    if ("trn_"+str(tx)+"_"+str(ty) in self.combatants) and (self.combatants["trn_"+str(tx)+"_"+str(ty)].side=="_tr"):
                        if self.combatants["trn_"+str(tx)+"_"+str(ty)].combatant=="Locomotive":
                            self.marked_tile=(tx, ty)
                            self.mark_valid_rails(self.transarctica_combat_train,self.marked_tile[1],4)
                        elif self.combatants["trn_"+str(tx)+"_"+str(ty)].stat["spawn"]!="na": 
                            self.marked_tile=(tx, ty)
                            self.mark_valid_move_squares(self.marked_tile,0,1)
                            self.spawn_unit=self.combatants["trn_"+str(tx)+"_"+str(ty)].stat["spawn"]
                        elif self.combatants["trn_"+str(tx)+"_"+str(ty)].combatant=="Machine gun": 
                            self.marked_tile=(tx, ty)
                            self.mark_valid_move_squares(self.marked_tile,0,0)
                            self.mark_valid_range_combat_squares(self.combatants["trn_"+str(tx)+"_"+str(ty)].stat["max_range"],8)
                        elif self.combatants["trn_"+str(tx)+"_"+str(ty)].combatant=="Cannon": 
                            self.marked_tile=(tx, ty)
                            self.mark_valid_move_squares(self.marked_tile,0,0)
                            max_range=self.combatants["trn_"+str(tx)+"_"+str(ty)].stat["max_range"]
                            self.mark_valid_range_combat_squares(abs(max_range),16)
                            if max_range<0:
                                self.mark_valid_indirect_combat_squares(abs(max_range))

                        else:
                            self.marked_tile=(tx, ty)
                            combat_unit = self.combatants["trn_"+str(tx)+"_"+str(ty)]
                            self.bracket_sel.x=(self.marked_tile[0])*tw
                            self.bracket_sel.y=(self.marked_tile[1])*tw
                            self.mark_valid_move_squares(self.marked_tile,0,combat_unit.stat["max_move"])
                            if combat_unit.stat["max_range"]>1:
                                self.remove_combat_squares()
                                self.mark_valid_range_combat_squares(combat_unit.stat["max_range"],4)
                else:
                    if (self.marked_tile!=(tx,ty)):
                        if ("trn_"+str(tx)+"_"+str(ty) in self.valid_squares): 
                            if self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="move":
                                if self.spawn_unit!="na":
                                    
                                    self.spawn_unit="na"
                                if ("trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1]) in self.combatants) and (self.combatants["trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1])].combatant=="Locomotive"):
                                    self.move_path.clear()                
                                    dist=int(cell[tx][ty].properties["dist"])
                                    self.move_combat_train(self.transarctica_combat_train,dist,ty)
                                    self.clear_valid_squares()
                                else:
                                    self.move_path.clear()                
                                    self.create_move_path((tx,ty))
                                    self.move_combat_unit_blocked(self.move_path)
                                    self.clear_valid_squares()

                            else:
# self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="melee" or self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="ranged" or self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="indirect":
                                combat_unit = self.combatants["trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1])]
                                if self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="melee":
                                    self.move_path.clear()                
                                    self.create_move_path((tx,ty))
                                    if self.attack_combat_unit_close(tx,ty):
                                        self.move_combat_unit_blocked(self.move_path)
                                if self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="ranged":
                                    self.attack_combat_unit_ranged(tx,ty)
                                if self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]=="indirect":
                                    self.attack_combat_unit_ranged(tx,ty)
                                self.clear_valid_squares()
                    else: 
                        self.clear_valid_squares()
            elif buttons == 4:  # 1: left, 2: middle etc.
                self.clear_valid_squares()

                #self.map.add(Sprite(self.gallery.content["back"]["pos"], position=((tx+0.5)*tw,(ty+0.5)*tw )), name="back_right_click")
                #self.map.add(Label(cell[tx][ty].properties["dist"], ((tx+0.5)*tw,(ty+0.5)*tw ), color=(25,50,75,255), font_name="Arial", bold=True, font_size=15, anchor_x="center", anchor_y="center"), name="label_right_click")

    def get_scroll_offset_x(self):
        current_middle = self.pixel_from_screen(int(director.window.width/2), int((director.window.height+self.viewport_height)/2))
        return current_middle[0]-self.base_middle[0]


    def mark_valid_range_combat_squares(self,max_range,scan_step):
        tw=self.map.tw
        LOS_Start=self.map.cells[self.marked_tile[0]][self.marked_tile[1]].center
        LOS_Start=(LOS_Start[0]-(self.get_scroll_offset_x()),LOS_Start[1]+100 )
        self.LOS.start=LOS_Start 
        r=max_range*tw
        for xx in range(-r, +r, scan_step):#(r*2)//10):
            yy=sqrt((r*r)-(xx*xx))

            ccx, ccy = director.get_virtual_coordinates(xx+LOS_Start[0], yy+LOS_Start[1])
            ctx = int((ccx + self.map.view_x) / tw)
            cty = int((ccy + self.map.view_y-self.viewport_height) / tw)
            self.check_LOS((trunc(ccx), trunc(ccy)))

            ccx, ccy = director.get_virtual_coordinates(xx+LOS_Start[0], -yy+LOS_Start[1])
            ctx = int((ccx + self.map.view_x) / tw)
            cty = int((ccy + self.map.view_y-self.viewport_height) / tw)
            self.check_LOS((trunc(ccx), trunc(ccy)))

    def mark_valid_indirect_combat_squares(self,max_range):
        tw=self.map.tw
        attacking_unit = self.combatants["trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1])]
        for co in self.combatants: 
            if self.combatants[co].side!=attacking_unit.side:
                defending_unit=self.combatants[co]
                ax, ay=self.marked_tile
                aa=(co[4:15])
                bb=aa.find("_")      
                dx=int(aa[0:bb]) 
                dy=int(aa[bb+1:15])   
                r=trunc(sqrt((ax-dx)*(ax-dx)+(ay-dy)*(ay-dy)))
                if r<=max_range:
                    if co not in self.valid_squares:
                        self.valid_squares[co]={}
                        self.valid_squares[co]["dist"]=r
                        self.valid_squares[co]["type"]="indirect"
                        square = Sprite(self.gallery.content["trn"]["valid_square_"+self.valid_squares[co]["type"]], position=(((dx+0.5)*self.map.tw, (dy+0.5)*self.map.tw)))
                        self.valid_squares[co]["sprite"]=square
                        self.valid_squares[co]["pos"]=(dx,dy)
                        self.map.add(square)

    def check_LOS(self,target):
        self.LOS.end=target
        tw=self.map.tw
        cell=self.map.cells

        if abs(self.LOS.start[0]-self.LOS.end[0]) > abs(self.LOS.start[1]-self.LOS.end[1]):
            axis=0
        else:
            axis=1
    
        if self.LOS.start[axis]>self.LOS.end[axis]:
            step=-4
        else:
            step=4
        cc=(-1,-1)

        for pa in range(self.LOS.start[axis], self.LOS.end[axis],step ):
            if axis==0:
                px=pa
                py=(((self.LOS.end[1]-self.LOS.start[1])*(px-self.LOS.start[0]))//(self.LOS.end[0]-self.LOS.start[0]))+self.LOS.start[1]
            else:
                py=pa
                px=(((self.LOS.end[0]-self.LOS.start[0])*(py-self.LOS.start[1]))//(self.LOS.end[1]-self.LOS.start[1]))+self.LOS.start[0]
            
            cx, cy = director.get_virtual_coordinates(px, py)
            ctx = int((cx + self.map.view_x) / tw)
            cty = int((cy + self.map.view_y-self.viewport_height) / tw)

            if cc!=(ctx,cty):
                cc=(ctx,cty)
                if (ctx<0) or (ctx>=len(cell)) or (cty<0) or (cty>=len(cell[ctx])) or cell[ctx][cty].properties["terrain"]=="h":
                    break
                else:  
                    if ("trn_"+str(ctx)+"_"+str(cty) not in self.valid_squares):
                        if ("trn_"+str(ctx)+"_"+str(cty) in self.combatants) and (self.combatants["trn_"+str(ctx)+"_"+str(cty)].side=="_vu"):  
                            self.valid_squares["trn_"+str(ctx)+"_"+str(cty)]={}
                            self.valid_squares["trn_"+str(ctx)+"_"+str(cty)]["dist"]=99
                            cell[ctx][cty].properties["dist"]=99
                            self.valid_squares["trn_"+str(ctx)+"_"+str(cty)]["type"]="ranged"
                            square = Sprite(self.gallery.content["trn"]["valid_square_"+self.valid_squares["trn_"+str(ctx)+"_"+str(cty)]["type"]], position=(((ctx+0.5)*self.map.tw, (cty+0.5)*self.map.tw)))
                            self.valid_squares["trn_"+str(ctx)+"_"+str(cty)]["sprite"]=square
                            self.valid_squares["trn_"+str(ctx)+"_"+str(cty)]["pos"]=(ctx,cty)
                            self.map.add(square)

           
    def mark_valid_rails(self,combat_train,py,maxdist):
        cell=self.map.cells
        for tx in range(1,len(cell)-1,1):
            if (("trn_"+str(tx-1)+"_"+str(py) in self.combatants) and (self.combatants["trn_"+str(tx-1)+"_"+str(py)].combatant=="Locomotive")) and (("trn_"+str(tx)+"_"+str(py) in self.combatants) and (self.combatants["trn_"+str(tx)+"_"+str(py)].combatant!="Locomotive")):
                for addx in range(0,maxdist,1):
                    if combat_train.right_tx+addx<len(cell):
                        self.valid_squares["trn_"+str(tx+addx)+"_"+str(py)]={}
                        self.valid_squares["trn_"+str(tx+addx)+"_"+str(py)]["dist"]=addx+1
                        cell[tx+addx][py].properties["dist"]=str(addx+1)
                        self.valid_squares["trn_"+str(tx+addx)+"_"+str(py)]["type"]="move"
                        
                        square = Sprite(self.gallery.content["trn"]["valid_square_"+self.valid_squares["trn_"+str(tx+addx)+"_"+str(py)]["type"]], position=(((tx+addx+0.5)*self.map.tw, (py+0.5)*self.map.tw)))
                        self.valid_squares["trn_"+str(tx+addx)+"_"+str(py)]["sprite"]=square
                        self.valid_squares["trn_"+str(tx+addx)+"_"+str(py)]["pos"]=(tx+addx,py)
                        self.map.add(square)
                    
        for tx in range(len(cell)-2,1,-1):
            if (("trn_"+str(tx+1)+"_"+str(py) in self.combatants) and (self.combatants["trn_"+str(tx+1)+"_"+str(py)].combatant=="Locomotive")) and (("trn_"+str(tx)+"_"+str(py) in self.combatants) and (self.combatants["trn_"+str(tx)+"_"+str(py)].combatant!="Locomotive")):
                for addx in range(0,maxdist,1):
                    if combat_train.left_tx-addx>0:
                        self.valid_squares["trn_"+str(tx-addx)+"_"+str(py)]={}
                        self.valid_squares["trn_"+str(tx-addx)+"_"+str(py)]["dist"]=-addx-1
                        cell[tx-addx][py].properties["dist"]=str(-addx-1)
                        self.valid_squares["trn_"+str(tx-addx)+"_"+str(py)]["type"]="move"
                       
                        square = Sprite(self.gallery.content["trn"]["valid_square_"+self.valid_squares["trn_"+str(tx-addx)+"_"+str(py)]["type"]], position=(((tx-addx+0.5)*self.map.tw, (py+0.5)*self.map.tw)))
                        self.valid_squares["trn_"+str(tx-addx)+"_"+str(py)]["sprite"]=square
                        self.valid_squares["trn_"+str(tx-addx)+"_"+str(py)]["pos"]=(tx-addx,py)
                        self.map.add(square)


    def move_combat_train(self,combat_train,dist,py):
        cell=self.map.cells
        rx=combat_train.right_tx
        combat_train.move_train(dist,(rx+dist,py),True)
        combat_train.right_tx+=dist
        combat_train.left_tx+=dist
        for tx in range(0, len(cell),1):
            if ("trn_"+str(tx)+"_"+str(py)) in self.combatants: 
                if self.combatants["trn_"+str(tx)+"_"+str(py)].stat["type"]=="wagon":
                    self.combatants.pop("trn_"+str(tx)+"_"+str(py))
        for i in range(0,len(self.transarctica_combat_train_layout),1):
            self.combatants["trn_"+str(i+combat_train.left_tx)+"_"+str(py)]=self.transarctica_combat_train_layout[i]


    def mark_valid_move_squares(self,ppos,dist, maxdist):
        cell=self.map.cells
        tx,ty=ppos
        if (tx>=0) and (tx<len(cell)) and (ty>=0) and (ty<len(cell[tx])):
            if ppos==self.marked_tile:
                dist=0
            else:
                dist+=self.combatants["trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1])].stat["move_modifiers"][cell[tx][ty].properties["terrain"]]
            
            cell_friendly=("trn_"+str(tx)+"_"+str(ty) in self.combatants) and (self.combatants["trn_"+str(tx)+"_"+str(ty)].side=="_tr")

            if ("trn_"+str(tx)+"_"+str(ty) not in self.valid_squares) and (dist<=maxdist) and (not(cell_friendly) or (ppos==self.marked_tile )):
                self.valid_squares["trn_"+str(tx)+"_"+str(ty)]={}
                self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["dist"]=dist
                cell[tx][ty].properties["dist"]=str(dist)
                if ("trn_"+str(tx)+"_"+str(ty) in self.combatants):
                    if (self.combatants["trn_"+str(tx)+"_"+str(ty)].side=="_vu"):  
                        self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]="melee"
                    elif (self.combatants["trn_"+str(tx)+"_"+str(ty)].side=="_tr"):
                        self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]="move"
                else:
                    self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]="move"

                square = Sprite(self.gallery.content["trn"]["valid_square_"+self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["type"]], position=(((tx+0.5)*self.map.tw, (ty+0.5)*self.map.tw)))
                self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["sprite"]=square
                self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["pos"]=(tx,ty)
                self.map.add(square)
                for ta in self.adjacent_tiles:
                    dx, dy=self.adjacent_tiles[ta]
                    self.mark_valid_move_squares((tx+dx, ty+dy), dist, maxdist)
            elif  ("trn_"+str(tx)+"_"+str(ty) in self.valid_squares) and (self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["dist"]>dist):
                self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["dist"]=dist
                cell[tx][ty].properties["dist"]=str(dist)
                for ta in self.adjacent_tiles:
                    dx, dy=self.adjacent_tiles[ta]
                    self.mark_valid_move_squares((tx+dx, ty+dy), dist,maxdist)
       
    def remove_combat_squares(self):
        to_be_popped=[]
        for sq in self.valid_squares:
            if self.valid_squares[sq]["type"]=="melee":
                to_be_popped.append(sq)
        for sq in to_be_popped:
            tx,ty=self.valid_squares[sq]["pos"]
            self.map.cells[tx][ty].properties["dist"]="9999"
            self.map.remove(self.valid_squares[sq]["sprite"])                   
            self.valid_squares.pop(sq) 
        to_be_popped.clear() 
     
    def clear_valid_squares(self):
        for trn in self.valid_squares:
            tx,ty=self.valid_squares[trn]["pos"]
            self.map.cells[tx][ty].properties["dist"]="9999"
            self.map.remove(self.valid_squares[trn]["sprite"])
        self.valid_squares.clear()
        self.marked_tile=(-10,-10)
        self.bracket_sel.x=(self.marked_tile[0])*self.map.tw
        self.bracket_sel.y=(self.marked_tile[1])*self.map.tw
        self.bracket.image=self.gallery.content["trn"]["bracket"]


    def attack_combat_unit_close(self,mx,my):
        defending_unit = self.combatants["trn_"+str(mx)+"_"+str(my)]
        attacking_unit = self.combatants["trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1])]
        defense_force = 0      
        offense_force = 0

        if self.map.cells[mx][my].properties["terrain"]=="f":
            defense_force += random.randint(0, 5)
            offense_force -= random.randint(0, 5)
        if self.map.cells[self.marked_tile[0]][self.marked_tile[1]].properties["terrain"]=="f":
            defense_force -= random.randint(0, 5)
            offense_force += random.randint(0, 5)
        
        offense_force+=attacking_unit.force-5+random.randint(0, 10)
        defense_force+=defending_unit.force-5+random.randint(0, 10)

        offense_force=max(0,offense_force)
        defense_force=max(0,defense_force)

        print(str(attacking_unit.force)+" "+str(offense_force)+" "+str(defending_unit.force)+" "+str(defense_force))
        attacking_unit.recalculate_force(-defense_force)
        defending_unit.recalculate_force(-offense_force)
        print(str(attacking_unit.force)+" "+str(offense_force)+" "+str(defending_unit.force)+" "+str(defense_force))
        if attacking_unit.force<=0:
            self.combatants.pop("trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1]))
            self.map.remove(attacking_unit)
        if defending_unit.force<=0:
            self.combatants.pop("trn_"+str(mx)+"_"+str(my))
            self.map.remove(defending_unit)
        if (attacking_unit.force>0) and (defending_unit.force<=0):
            return True
        else:
            return False

    def attack_combat_unit_ranged(self,mx,my):
        defending_unit = self.combatants["trn_"+str(mx)+"_"+str(my)]
        attacking_unit = self.combatants["trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1])]
        defense_force = 0      
        offense_force = 0

        if self.map.cells[mx][my].properties["terrain"]=="f":
            defense_force += random.randint(0, 5)
            offense_force -= random.randint(0, 5)
        if self.map.cells[self.marked_tile[0]][self.marked_tile[1]].properties["terrain"]=="f":
            defense_force -= random.randint(0, 5)
            offense_force += random.randint(0, 5)
        
        offense_force+=attacking_unit.force-5+random.randint(0, 10)
        defense_force+=defending_unit.force-5+random.randint(0, 10)

        offense_force=trunc(max(0,offense_force/2))
        defense_force=trunc(max(0,defense_force/2))
        if defending_unit.stat["max_range"]<=1 or defending_unit.stat["max_range"]<self.valid_squares["trn_"+str(mx)+"_"+str(my)]["dist"]:
            defense_force=0

        print(str(attacking_unit.force)+" "+str(offense_force)+" "+str(defending_unit.force)+" "+str(defense_force))
        attacking_unit.recalculate_force(-defense_force)
        defending_unit.recalculate_force(-offense_force)
           
        if defending_unit.stat["type"]=="wagon":
            if defending_unit.side=="_tr":
                self.transarctica_combat_train.wagon_damaged(defending_unit.wagon_id,defending_unit.wagon_width, defending_unit.force)
            else:
                self.vu_combat_train.wagon_damaged(defending_unit.wagon_id,defending_unit.wagon_width, defending_unit.force)
            
        print(str(attacking_unit.force)+" "+str(offense_force)+" "+str(defending_unit.force)+" "+str(defense_force))
        if attacking_unit.force<=0:
            self.combatants.pop("trn_"+str(self.marked_tile[0])+"_"+str(self.marked_tile[1]))
            self.map.remove(attacking_unit)
        if defending_unit.force<=0:
            if defending_unit.stat["type"]=="unit":
                self.combatants.pop("trn_"+str(mx)+"_"+str(my))
                self.map.remove(defending_unit)
            elif defending_unit.stat["type"]=="wagon":
                to_be_popped=[]
                for co in self.combatants:
                    if self.combatants[co]==defending_unit:
                        to_be_popped.append(co)
                for co in to_be_popped:
                    self.combatants.pop(co) 
                to_be_popped.clear() 
                #if defending_unit.side=="_tr":
                #    self.transarctica_combat_train.wagon_damaged(defending_unit.wagon_id,defending_unit.wagon_width, defending_unit.force)
                #else:
                #    self.vu_combat_train.wagon_damaged(defending_unit.wagon_id,defending_unit.wagon_width, defending_unit.force)



    def move_combat_unit_blocked(self,path):
        tstart=path[0]
        tdest=path[len(path)-1]
        combat_unit = self.combatants["trn_"+str(tstart[0])+"_"+str(tstart[1])]
        self.combatants["trn_"+str(tdest[0])+"_"+str(tdest[1])]=combat_unit
        self.combatants.pop("trn_"+str(tstart[0])+"_"+str(tstart[1]))
        combat_unit.move_unit_blocked(path,True)


    def create_move_path(self,ppos):
        self.move_path.append(ppos)
        if not(ppos == self.marked_tile):
            tx,ty=ppos
            cdist=self.valid_squares["trn_"+str(tx)+"_"+str(ty)]["dist"]
            for ta in self.adjacent_tiles:
                dx, dy=self.adjacent_tiles[ta]
                if ("trn_"+str(tx+dx)+"_"+str(ty+dy) in self.valid_squares) and (self.valid_squares["trn_"+str(tx+dx)+"_"+str(ty+dy)]["dist"]<cdist):
                    self.create_move_path((tx+dx,ty+dy))
                    break
        else:
            self.move_path.reverse()

        

    def on_mouse_release(self, x, y, buttons, modifiers):
        try:
            if buttons == 4:  # 1: left, 2: middle etc.
                self.map.remove("label_right_click")
                self.map.remove("back_right_click")
        except:
            A=1


    def scroll(self, dt):
        current_middle = self.pixel_from_screen(int(director.window.width/2), int((director.window.height+self.viewport_height)/2))
        self.set_focus(current_middle[0] + self.scroll_direction[0]*dt, current_middle[1] + self.scroll_direction[1]*dt)

    def update_properties(self):
        for x in self.map.cells:
            for y in x:
                if y.tile is None:
                    continue
                y.properties.update(y.tile.properties)

            #if False:
            #    self.LOS.end=(x,y)
            #    if abs(self.LOS.start[0]-self.LOS.end[0]) > abs(self.LOS.start[1]-self.LOS.end[1]):
            #        axis=0
            #    else:
            #        axis=1
            #    
            #    if self.LOS.start[axis]>self.LOS.end[axis]:
            #        step=-4
            #    else:
            #        step=4
            #    cc=(-1,-1)
            #    
            #    for pa in self.fire_path:
            #        self.map.remove(pa)
            #    self.fire_path.clear()
            #    for pa in range(self.LOS.start[axis], self.LOS.end[axis],step ):
            #        if axis==0:
            #            px=pa
            #            py=(((self.LOS.end[1]-self.LOS.start[1])*(px-self.LOS.start[0]))//(self.LOS.end[0]-self.LOS.start[0]))+self.LOS.start[1]
            #        else:
            #            py=pa
            #            px=(((self.LOS.end[0]-self.LOS.start[0])*(py-self.LOS.start[1]))//(self.LOS.end[1]-self.LOS.start[1]))+self.LOS.start[0]
            #        fire_range=tw*4 - sqrt(((px-self.LOS.start[0])*(px-self.LOS.start[0]))+((py-self.LOS.start[1])*(py-self.LOS.start[1])))
            #        if fire_range>0:
            #            cx, cy = director.get_virtual_coordinates(px, py)
            #            ctx = int((cx + self.map.view_x) / tw)
            #            cty = int((cy + self.map.view_y-self.viewport_height) / tw)
            #            if cc!=(ctx,cty):
            #                square = Sprite(self.gallery.content["trn"]["valid_square_combat"], position=(((ctx+0.5)*self.map.tw, (cty+0.5)*self.map.tw)))
            #                self.map.add(square)
            #                self.fire_path.append(square)  
            #                cc=(ctx,cty)  
            #            if (cell[ctx][cty].properties["terrain"]=="h"):
            #                self.LOS.end=(cx,cy)
            #                ctx=-1
            #                cty=-1
            #                break
            #print((ctx,cty))
