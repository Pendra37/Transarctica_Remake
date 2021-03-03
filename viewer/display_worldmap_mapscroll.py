# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import ScrollingManager
from cocos.sprite import Sprite
from controller import events
from . import TransarcticaActor
from . import VUTrainActor
from . import RoamerActor
from . import Gallery
from model import Config
import random
from cocos.rect import Rect
from cocos.text import Label


class DisplayWorldmapMapscroll(ScrollingManager):
    """edge scrollable scrolling manager"""
    def __init__(self, viewport_h):
        """
        initializer
        """

        self.viewport_height=viewport_h
        viewport=Rect(0,self.viewport_height,director.window.width,director.window.height-self.viewport_height) #director.window
        ScrollingManager.__init__(self, viewport)
        self.config = Config()
        self.gallery = Gallery()
        self.is_event_handler = True

        # scrolling
        self.inscroll=False
        self.scroll_direction = ()
        if len(self.config.loaded_objects)>0:
            self.POI=self.config.loaded_objects["POI"]
        else:
            self.POI = {}
           
        self.transarctica_actor = TransarcticaActor(self)
        self.transarctica = director.core.query_mover("Transarctica")
        self.vutrain=[]
        self.vutrain_actor = []
        for id in range(self.config.vutrain_count):
            self.vutrain_actor.append(id)
            self.vutrain_actor[id]=VUTrainActor(self,id)
            self.vutrain.append(id)
            self.vutrain[id]=director.core.query_mover("VUTrain"+str(id))
        self.roamer=[]
        self.roamer_actor = []
        for id in range(self.config.roamer_count):
            self.roamer_actor.append(id)
            self.roamer_actor[id]=RoamerActor(self,id)
            self.roamer.append(id)
            self.roamer[id]=director.core.query_mover("Roamer"+str(id))

    def set_visibility(self, vis):        
        return True

    def _break_set(self):
        self.transarctica_actor.stop()

    def _break_release(self):
        self.transarctica_actor.start()

    def _turn_back(self):
        self.transarctica_actor.turn_back()

    def add_transarctica(self):
        self.get("hidden objects").add(self.transarctica_actor)
        if self.transarctica_actor.is_break_released:
            self.transarctica_actor.start()
        self.place_player()
        self.find_engine()

    def add_vutrain(self, id):
        self.get("hidden objects").add(self.vutrain_actor[id])
        self.vutrain_actor[id].start()
        self.place_vutrain(id)

    def add_roamer(self, id):
        self.get("hidden objects").add(self.roamer_actor[id])
        self.roamer_actor[id].start()
        self.place_roamer(id)

    def place_player(self):
        x = self.transarctica.current_position["X"]
        y = self.transarctica.current_position["Y"]
        rails = self.get("hidden objects")
        self.transarctica_actor.position = rails.cells[x][y].center
        cell = self.get("rails").cells[x][y]
        direction = cell.properties["directions"]
        if not (self.transarctica.direction in direction):
            self.transarctica.direction = direction[0]

    def place_vutrain(self,id):
        x = self.vutrain_actor[id].vutrain.current_position["X"]
        y = self.vutrain_actor[id].vutrain.current_position["Y"]
        rails = self.get("hidden objects")
        self.vutrain_actor[id].position = rails.cells[x][y].center
        cell = self.get("rails").cells[x][y]
        direction = cell.properties["directions"]
        if not (self.vutrain_actor[id].vutrain.direction in direction):
            self.vutrain_actor[id].vutrain.direction = direction[0]

    def place_roamer(self,id):
        x = self.roamer_actor[id].roamer.current_position["X"]
        y = self.roamer_actor[id].roamer.current_position["Y"]
        rails = self.get("hidden objects")
        self.roamer_actor[id].position = rails.cells[x][y].center
        #cell = self.get("rails").cells[x][y]
        #direction = cell.properties["directions"]
        #if not (self.vutrain[id].direction in direction):
        #    self.vutrain[id].direction = direction[0]
        #print(self.vutrain[id].direction)

    def check_map_events(self, x, y):
        cell = self.get("rails").cells[x][y]
        if "city" in cell.properties:
            self.transarctica.last_event_position["X"]=x
            self.transarctica.last_event_position["Y"]=y
            return "arrive_at_city"
        if cell.tile:
            if "speedmod" in cell.properties:
                if self.check_tunnel_block():
                    self.transarctica.last_event_position["X"]=x
                    self.transarctica.last_event_position["Y"]=y
                    return "tunnel_block"  
            if "bridge" in cell.properties:
                if cell.properties["damaged"]=="Y":
                    self.transarctica.last_event_position["X"]=x
                    self.transarctica.last_event_position["Y"]=y
                    return "bridge_out"
            if "monster" in cell.properties:
                if self.check_bridge_monster():
                    self.transarctica.last_event_position["X"]=x
                    self.transarctica.last_event_position["Y"]=y
                    return "bridge_monster"  
            if "coal_mine" in cell.properties:
                if cell.properties["coal_mine"]>0: 
                    self.transarctica.last_event_position["X"]=x
                    self.transarctica.last_event_position["Y"]=y
                    return "coal_mine" 
        else:
            next_x = x + self.transarctica_actor.velocity_multipliers[self.transarctica.direction][0]
            next_y = y + self.transarctica_actor.velocity_multipliers[self.transarctica.direction][1]
            if ("directions" in self.get("rails").cells[next_x][next_y].properties):
                self.transarctica.last_event_position["X"]=x
                self.transarctica.last_event_position["Y"]=y
                return "bridge_out"
            else:
                self.transarctica.last_event_position["X"]=x
                self.transarctica.last_event_position["Y"]=y
                return "end_of_rail"  

    def check_map_events_vutrain(self, x, y):
        cell = self.get("rails").cells[x][y]
        if cell.tile:
            if "bridge" in cell.properties:
                if cell.properties["damaged"]=="Y":
                    return "bridge_out"
        else:
            return "end_of_rail"  
 

    def check_tunnel_block(self):
        self.config.tunnel_block_chance+=random.randint(0, 1)
        i=random.randint(1, 500)
        if i<self.config.tunnel_block_chance:
            self.config.tunnel_block_chance=0
            if (self.config.conf_wagons[self.transarctica.train_layout[len(self.transarctica.train_layout)-1]].storage=="drill") or (self.config.conf_wagons[self.transarctica.train_layout[0]].storage=="drill"):
                return False
            else:
                return True
        else:
            return False

    def check_bridge_monster(self):
        i=random.randint(1, 100)
        if i<33:
            return (self.transarctica.storage_cap["harpoon"]["max"]<=0)
        else:
            return False

    def build_bridge_on_map(self):
        tile_x = self.transarctica.last_event_position["X"]
        tile_y = self.transarctica.last_event_position["Y"]
        cell = self.get("rails").cells[tile_x][tile_y]
        if cell.tile and "bridge" in cell.properties and cell.properties["damaged"]=="Y":
            cell.properties["damaged"]="N"   
            bridge = Sprite(self.gallery.content["bridge"][cell.tile.properties["directions"]], position=((tile_x+0.5)*self.get("rails").tw,(tile_y+0.5)*self.get("rails").tw ))
            self.get("rails").add(bridge, name="bridge_"+str(tile_x)+"_"+str(tile_y))
      

    def find_engine(self):
        self.parent.change_displays("")
        self.set_focus(self.transarctica.current_position["X"] * 64, self.transarctica.current_position["Y"] * 64)
        

    def add_cities(self):
        self.update_properties()
        for tx, x in enumerate(self.get("rails").cells):
            for ty, y in enumerate(x):
                try: 
                    city_loc = str(tx)+","+str(ty)
                    self.get("rails").cells[int(Config.conf_cities_by_tile[city_loc].event_x)][int(Config.conf_cities_by_tile[city_loc].event_y)].properties["city"] = city_loc
                    if Config.conf_cities_by_tile[city_loc].type == "viking" or Config.conf_cities_by_tile[city_loc].type == "service":
                        citysprite_name = Config.conf_cities_by_tile[city_loc].type
                    else:
                        citysprite_name="generic"
                    city_w=int(Config.conf_cities_by_tile[city_loc].width)
                    city_h=int(Config.conf_cities_by_tile[city_loc].height)
                    citysprite = Sprite(self.gallery.content["city"][citysprite_name], position=(((tx+(city_w//3)+1)*self.get("rails").tw-(32*(city_w%2)), (ty+(city_h//3)+1)*self.get("rails").tw-(32*(city_h%2)))))
                    self.get("rails").add(citysprite)
                    if not(Config.conf_cities_by_tile[city_loc].type == "viking" or Config.conf_cities_by_tile[city_loc].type == "service"):
                        self.get("rails").add(Label(Config.conf_cities_by_tile[city_loc].name, ((tx+1.5)*self.get("rails").tw,(ty+0)*self.get("rails").tw ), color=(25,50,75,255), italic=True, bold=True, font_name="Arial", font_size=12, anchor_x="center", anchor_y="bottom"), name="label_city_"+city_loc)
                except:
                    A = 1

    def register_events(self):
        """puts switches and cities on the map"""
        self.update_properties()

        for tx, x in enumerate(self.get("rails").cells):
            for ty, y in enumerate(x):
                cell = self.get("rails").cells[tx][ty]
                
                if y.tile and "switch" in y.properties:
                    if len(self.config.loaded_objects)>0:
                        for id in self.POI:
                            if self.POI[id]["px"]==tx and self.POI[id]["py"]==ty and self.POI[id]["type"]=="switch" and self.POI[id]["status"]=="on":
                                self.switch_switch(tx,ty)
                    else:
                        self.POI[len(self.POI)]={"px":tx, "py":ty, "type": "switch", "status":"off" }
   
                if y.tile and "bridge" in y.properties:
                    if len(self.config.loaded_objects)>0:
                        for id in self.POI:
                            if self.POI[id]["px"]==tx and self.POI[id]["py"]==ty and self.POI[id]["type"]=="bridge":
                                y.properties["damaged"]=self.POI[id]["status"]
                                if self.POI[id]["status"]=="N":
                                    bridge = Sprite(self.gallery.content["bridge"][y.tile.properties["directions"]], position=((tx+0.5)*self.get("rails").tw,(ty+0.5)*self.get("rails").tw ))
                                    self.get("rails").add(bridge, name="bridge_"+str(tx)+"_"+str(ty))
                    else:
                        if y.properties["damaged"]=="N":
                            bridge = Sprite(self.gallery.content["bridge"][y.tile.properties["directions"]], position=((tx+0.5)*self.get("rails").tw,(ty+0.5)*self.get("rails").tw ))
                            self.get("rails").add(bridge, name="bridge_"+str(tx)+"_"+str(ty))
                        self.POI[len(self.POI)]={"px":tx, "py":ty, "type": "bridge", "status":y.properties["damaged"] }
                   
                # process cities
                if "event" in y.properties:
                    if y.properties["event"] == "city":
                        neighbours = [{"X": tx,   "Y": ty+1},
                                      {"X": tx+1, "Y": ty  },
                                      {"X": tx,   "Y": ty-1},
                                      {"X": tx-1, "Y": ty  }]
                        # the following long if is split to statements for only better readability
                        # city property is added only if all passed
                        for neighbour in neighbours:
                            if neighbour["X"] < 0 or neighbour["Y"] < 0:
                                continue
                            if len(self.get("rails").cells) > neighbour["X"]:  # check if column exist
                                if len(self.get("rails").cells[neighbour["X"]]) > neighbour["Y"]:  # check if row exist
                                    if self.get("rails").cells[neighbour["X"]][neighbour["Y"]].properties:  # check if has properties
                                        if "directions" in self.get("rails").cells[neighbour["X"]][neighbour["Y"]].properties:  # check if has directions
                                            if len(self.get("rails").cells[neighbour["X"]][neighbour["Y"]].properties["directions"]) == 1:  # check if bumper tile
                                                self.get("rails").cells[neighbour["X"]][neighbour["Y"]].properties["city"] = (tx, ty)



    def on_mouse_motion(self, x, y, dx, dy):
        """currently used for scrolling only"""
        x_thresholds = {"left": 20, "right": director.window.width-20}
        y_thresholds = {"down": 20, "up": director.window.height-20}
        step = Config.scroll_speed
        step_x = 0
        step_y = 0
        if x < x_thresholds["left"]: 
            step_x = step * (x - x_thresholds["left"])
        elif x > x_thresholds["right"]: 
            step_x = step * (x - x_thresholds["right"])
        if y < y_thresholds["down"]: 
            step_y = step * (y - y_thresholds["down"])
        elif y > y_thresholds["up"]:
            step_y = step * (y - y_thresholds["up"])
        if x <= 2 or x >= director.window.width-2:
            step_x=0
        if y <= 2 or y >= director.window.height-2:
            step_y=0
        if step_x != 0 or step_y != 0:
            self.scroll_direction = (step_x, step_y)
            self.inscroll=True
        else:
            self.scroll_direction = ()
            self.inscroll=False

    def on_mouse_press(self, x, y, buttons, modifiers):
        """event handler"""
        if buttons == 1:  # 1: left, 2: middle etc.
            current_x, current_y = director.get_virtual_coordinates(x, y)
            tile_x = int((current_x + self.get("rails").view_x) / self.get("rails").tw)
            tile_y = int((current_y + self.get("rails").view_y-self.viewport_height) / self.get("rails").tw)
            if tile_x < 0 or tile_y < 0 or tile_x >= len(self.get("rails").cells) or tile_y >= len(self.get("rails").cells[tile_x]):
                return  # click outside map
            self.switch_switch(tile_x,tile_y)
        if buttons == 4:  # 1: left, 2: middle etc.
            current_x, current_y = director.get_virtual_coordinates(x, y)
            tile_x = int((current_x + self.get("rails").view_x) / self.get("rails").tw)
            tile_y = int((current_y + self.get("rails").view_y-self.viewport_height) / self.get("rails").tw)
            self.get("rails").add(Sprite(self.gallery.content["back"]["pos"], position=((tile_x+0.5)*self.get("rails").tw,(tile_y+0.5)*self.get("rails").tw )), name="back_right_click")
            self.get("rails").add(Label(str(tile_x)+"/"+str(tile_y), ((tile_x+0.5)*self.get("rails").tw,(tile_y+0.5)*self.get("rails").tw ), color=(25,50,75,255), font_name="Arial", bold=True, font_size=15, anchor_x="center", anchor_y="center"), name="label_right_click")

    def on_mouse_release(self, x, y, buttons, modifiers):
        if buttons == 4:  # 1: left, 2: middle etc.
            self.get("rails").remove("label_right_click")
            self.get("rails").remove("back_right_click")

    def switch_switch(self, tile_x,tile_y):
            cell = self.get("rails").cells[tile_x][tile_y]
            if "switch" in cell.properties:
                if cell.properties["switch"] == "on":
                    cell.properties["switch"] = "off"
                    self.get("rails").remove("switch_"+str(tile_x)+"_"+str(tile_y))
                else:
                    cell.properties["switch"] = "on"
                    switch = Sprite(self.gallery.content["switch"][cell.tile.properties["directions"]], position=((tile_x+0.5)*self.get("rails").tw,(tile_y+0.5)*self.get("rails").tw ))
                    self.get("rails").add(switch, name="switch_"+str(tile_x)+"_"+str(tile_y))
                for id in self.POI:
                    if self.POI[id]["px"]==tile_x and self.POI[id]["py"]==tile_y and self.POI[id]["type"]=="switch":
                        self.POI[id]["status"]=cell.properties["switch"]
                    
                direction = cell.properties["directions"]
                new_direction = direction[0] + direction[2] + direction[1]
                self.get("rails").cells[tile_x][tile_y].properties["directions"] = new_direction


    def scroll(self):
        """scrolls according to the mouse's direction"""
        if self.inscroll:
            current_middle = self.pixel_from_screen(int(director.window.width/2), int((director.window.height+self.viewport_height)/2))
            self.set_focus(current_middle[0] + self.scroll_direction[0], current_middle[1] + self.scroll_direction[1])

    def update_properties(self):
        """
        Copies tile properties to cell properties. This is required to make
        cells function independently. Tileless cells are skipped.
        """
        for x in self.get("rails").cells:
            for y in x:
                if y.tile is None:
                    continue
                y.properties.update(y.tile.properties)

    def generate_coal_mines(self):
        if len(self.config.loaded_objects)>0:
            for id in self.POI:
                if self.POI[id]["type"]=="coal_mine":
                    cell = self.get("rails").cells[self.POI[id]["px"]][self.POI[id]["py"]]
                    cell.properties["coal_mine"]=self.POI[id]["status"]
        else:
            cnt=len(self.config.coal_mine)
            while cnt<self.config.coal_mine_count:
                x = random.randint(5, self.config.map_width-5)
                y = random.randint(5, self.config.map_height-5)
                cell = self.get("rails").cells[x][y]
                if cell.tile:
                    self.config.coal_mine[str(cnt*2)] = {} 
                    self.config.coal_mine[str(cnt*2)]["pos"]="X: "+str(x)
                    self.config.coal_mine[str(cnt*2)]["known"]=False
                    self.config.coal_mine[str(cnt*2)]["mined"]=False
                    self.config.coal_mine[str(cnt*2+1)] = {} 
                    self.config.coal_mine[str(cnt*2+1)]["pos"]="Y: "+str(y)
                    self.config.coal_mine[str(cnt*2+1)]["known"]=False
                    self.config.coal_mine[str(cnt*2+1)]["mined"]=False
                    cell.properties["coal_mine"]=random.randint(500, 5000)
                    self.POI[len(self.POI)]={"px":x, "py":y, "type": "coal_mine", "status":cell.properties["coal_mine"] }
                    cnt+=1

