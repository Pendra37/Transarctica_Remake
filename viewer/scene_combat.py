# -*- coding: utf-8 -*-
from cocos import tiles
from cocos.director import director
from cocos.scene import Scene
from model.config import Config
from .gallery import Gallery
from .display_worldmap_hud import DisplayWorldmapHUD
from .display_worldmap_engine import DisplayWorldmapEngine
from .display_worldmap_cnc import DisplayWorldmapCNC
from .display_worldmap_quarters import DisplayWorldmapQuarters
#from .display_worldmap_launcher import DisplayWorldmapLauncher
from .display_worldmap_minitrain import DisplayWorldmapMiniTrain
from .display_combat_mapscroll import DisplayCombatMapscroll
from cocos.layer import ColorLayer
from math import trunc
from pyglet.media import load
from pyglet.media import Player, SourceGroup

class SceneCombat(Scene):
    """loads the world map scene"""

    def __init__(self):
        """initializer"""
        Scene.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        # creating map
        raw_map = tiles.load("{}/{}.{}".format(self.config.resources, "combat", self.config.map_format) )
        self.tw = self.config.tile_width = raw_map.contents["combat"].tw

    
        snow_base = ColorLayer( 250, 250, 250, 255, director.window.width, director.window.height)
        self.add(snow_base, name="display_worldmap_snow")
        cz = 1
        self.add(DisplayCombatMapscroll(0), z=cz, name="display_combat_mapscroll")
        cz +=1
        padding_x, padding_y = self.get_initial_padding(raw_map)
        print('e')
        for layer_name in [ "combat"]:  # TODO remove this hardcoded stuff, where is the Z value?
            cz += 1
            self.get("display_combat_mapscroll").add(raw_map.contents[layer_name], z=cz, name=layer_name) #z=len(self.children), name=layer_name)
            self.get("display_combat_mapscroll").get(layer_name).set_view(padding_x, padding_y, director.window.width + padding_x, director.window.height + padding_y)
        print('e')
        cz +=1
        self.get("display_combat_mapscroll").init_tactical_map()
        print('e')
#        self.add(DisplayWorldmapLauncher(), z=cz, name="display_worldmap_launcher")
#        cz +=1
        self.MapInZoom=True
        print('e')
        self.display_combat_mapscroll=self.get("display_combat_mapscroll")    
        print('e')

        #self.schedule_interval(self.map_time_change, interval=1/30)
        #self.schedule(self.map_time_change)


    def map_time_change(self, dt):
        if self.config.time_speed:
            self.display_worldmap_hud.refresh_labels(dt) 
            self.display_worldmap_minitrain.refresh_labels() 
            self.display_worldmap_engine.refresh_labels() 
            self.display_worldmap_cnc.refresh_labels() 
            self.display_worldmap_quarters.refresh_labels() 
            self.display_combat_mapscroll.scroll()
            self.display_combat_mapscroll.transarctica_actor.update_actor(dt)

            for id in range(self.config.vutrain_count):  
                if self.display_combat_mapscroll.vutrain_actor[id].vutrain.is_intact:  
                    self.display_combat_mapscroll.vutrain_actor[id].update_actor(dt)
                else:
                    self.display_combat_mapscroll.vutrain_actor[id].spawn_randomly()
            for id in range(self.config.roamer_count):    
                self.display_combat_mapscroll.roamer_actor[id].update_actor(dt)
            time_change=trunc(director.core.timestamp*1440)-trunc(director.core.TSP*1440)
            if time_change>=1:
                self.display_combat_mapscroll.transarctica.update_telemetry(time_change)
                for id in range(self.config.vutrain_count):
                    self.display_combat_mapscroll.vutrain[id].update_telemetry(time_change)
                director.core.TSP=director.core.timestamp

    def get_initial_padding(self, raw_map):
        """for the start"""
        map = self.get("display_combat_mapscroll")
        map_size = {"X": raw_map.contents["combat"].px_width, "Y": raw_map.contents["combat"].px_height}
        padding_x = (director.window.width - map_size["X"]) / -2
        padding_y = (director.window.height - map_size["Y"]) / -2
        return padding_x, padding_y

    def get_tile_type(self, x, y):
        """returns the type of the selected tile"""
        return self.get("display_combat_mapscroll").get("combat").cells[x][y].tile.id - 1
        # Why minus 1 you may ask. Because Cocos assigns IDs starting from 1 not
        # from 0 so it gives all tiles ID 1 value higher than their true IDs are.

    def change_displays(self, display_to_show):
        if display_to_show !="":
            vis=self.get(display_to_show).visible
        self.get("display_worldmap_engine").set_visibility(False)
        self.get("display_worldmap_cnc").set_visibility(False)
        self.get("display_worldmap_quarters").set_visibility(False)
        #self.get("display_worldmap_launcher").set_visibility(False)
        if display_to_show !="":
            self.get(display_to_show).set_visibility(not(vis))
        #    self.get("display_combat_mapscroll").find_engine()
        if self.get("display_worldmap_engine").visible or self.get("display_worldmap_cnc").visible or self.get("display_worldmap_quarters").visible: 
             self.ambient.volume=0.15* self.config.sound_switch
        else:
             self.ambient.volume=0.3* self.config.sound_switch
        if self.get("display_worldmap_engine").visible: 
            self.move_sound="piston_"
        else:
            self.move_sound="speed_"


