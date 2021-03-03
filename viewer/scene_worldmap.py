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
from .display_worldmap_mapscroll import DisplayWorldmapMapscroll
from cocos.layer import ColorLayer
from math import trunc
from pyglet.media import load
from pyglet.media import Player, SourceGroup

class SceneWorldMap(Scene):
    """loads the world map scene"""

    def __init__(self, map_file):
        """initializer"""
        Scene.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        # creating map
        raw_map = tiles.load(map_file)
        self.tw = self.config.tile_width = raw_map.contents["rails"].tw

        self.ambient = Player()
        source = load("music/arctic_wind.wav")
        ambient_loop = SourceGroup(source.audio_format, None)
        ambient_loop.loop = True
        ambient_loop.queue(source)
        self.ambient.queue(ambient_loop)
        self.ambient.volume=0.3 * self.config.sound_switch
        self.ambient.play()

        self.move_sound="speed_"
        self.train_sound="speed_1"
        self.train_sounds = Player()
        source = load("music/"+self.train_sound+".wav")
        self.train_sounds_loop = SourceGroup(source.audio_format, None)
        self.train_sounds_loop.loop = True
        self.train_sounds_loop.queue(source)
        self.train_sounds.queue(self.train_sounds_loop)
        self.train_sounds.volume=0.7 * self.config.sound_switch


        minitrain=DisplayWorldmapMiniTrain()
        hud=DisplayWorldmapHUD()        
        snow_base = ColorLayer( 250, 250, 250, 255, director.window.width, director.window.height)
        self.add(snow_base, name="display_worldmap_snow")
        cz = 1
        self.add(DisplayWorldmapMapscroll(minitrain.optimal_height+hud.optimal_height), z=cz, name="display_worldmap_mapscroll")
        cz +=1
        padding_x, padding_y = self.get_initial_padding(raw_map)
        for layer_name in [ "objects", "connectors", "rails","hidden rails", "hidden objects"]:  # TODO remove this hardcoded stuff, where is the Z value?
            cz += 1
            self.get("display_worldmap_mapscroll").add(raw_map.contents[layer_name], z=cz, name=layer_name) #z=len(self.children), name=layer_name)
            self.get("display_worldmap_mapscroll").get(layer_name).set_view(padding_x, padding_y, director.window.width + padding_x, director.window.height + padding_y)
        
        self.get("display_worldmap_mapscroll").add_cities()
        self.get("display_worldmap_mapscroll").register_events()
        self.get("display_worldmap_mapscroll").generate_coal_mines()
        cz +=1
        self.add(minitrain, z=cz, name="display_worldmap_minitrain")
        cz +=1
        self.add(hud, z=cz, name="display_worldmap_hud")

        cz +=1
        self.add(DisplayWorldmapEngine(), z=cz, name="display_worldmap_engine")
        cz +=1
        self.add(DisplayWorldmapCNC(), z=cz, name="display_worldmap_cnc")
        cz +=1
        self.add(DisplayWorldmapQuarters(), z=cz, name="display_worldmap_quarters")
        cz +=1
#        self.add(DisplayWorldmapLauncher(), z=cz, name="display_worldmap_launcher")
#        cz +=1
        self.MapInZoom=True
        self.display_worldmap_mapscroll=self.get("display_worldmap_mapscroll")    
        self.display_worldmap_hud=self.get("display_worldmap_hud")    
        self.display_worldmap_minitrain=self.get("display_worldmap_minitrain")    
        self.display_worldmap_engine=self.get("display_worldmap_engine")    
        self.display_worldmap_cnc=self.get("display_worldmap_cnc")    
        self.display_worldmap_quarters=self.get("display_worldmap_quarters")    

        self.display_worldmap_mapscroll.add_transarctica()
        for id in range(self.config.vutrain_count):
            self.display_worldmap_mapscroll.add_vutrain(id)
        for id in range(self.config.roamer_count):
            self.display_worldmap_mapscroll.add_roamer(id)

        #self.schedule_interval(self.map_time_change, interval=1/30)
        self.schedule(self.map_time_change)


    def map_time_change(self, dt):
        if self.config.time_speed:
            self.display_worldmap_hud.refresh_labels(dt) 
            self.display_worldmap_minitrain.refresh_labels() 
            self.display_worldmap_engine.refresh_labels() 
            self.display_worldmap_cnc.refresh_labels() 
            self.display_worldmap_quarters.refresh_labels() 
            self.update_sounds()
            self.display_worldmap_mapscroll.scroll()
            self.display_worldmap_mapscroll.transarctica_actor.update_actor(dt)

            for id in range(self.config.vutrain_count):  
                if self.display_worldmap_mapscroll.vutrain_actor[id].vutrain.is_intact:  
                    self.display_worldmap_mapscroll.vutrain_actor[id].update_actor(dt)
                else:
                    self.display_worldmap_mapscroll.vutrain_actor[id].spawn_randomly()
            for id in range(self.config.roamer_count):    
                self.display_worldmap_mapscroll.roamer_actor[id].update_actor(dt)
            time_change=trunc(director.core.timestamp*1440)-trunc(director.core.TSP*1440)
            if time_change>=1:
                self.display_worldmap_mapscroll.transarctica.update_telemetry(time_change)
                for id in range(self.config.vutrain_count):
                    self.display_worldmap_mapscroll.vutrain[id].update_telemetry(time_change)
                director.core.TSP=director.core.timestamp

    def update_sounds(self):
        curr_speed=self.display_worldmap_mapscroll.transarctica_actor.transarctica.speed
        if curr_speed == 0:
            if self.train_sounds.playing:
                self.train_sounds.pause()
                self.train_sound=self.move_sound+"1"
        else:
            if curr_speed>240:
                new_sound=self.move_sound+"3"
            elif curr_speed>120:
                new_sound=self.move_sound+"2"
            elif curr_speed<=120:
                new_sound=self.move_sound+"1"
            if not self.train_sounds.playing:
                self.train_sounds.play()
                self.train_sound=""
            if self.train_sound!= new_sound:
                source = load("music/"+new_sound+".wav")
                self.train_sound = new_sound
                self.train_sounds_loop.queue(source)
                self.train_sounds_loop.next_source()




    def sound_off(self):
        self.ambient.pause()
        self.train_sounds.pause()

    def sound_on(self):
        self.ambient.play()

    def get_initial_padding(self, raw_map):
        """for the start"""
        map = self.get("display_worldmap_mapscroll")
        transarctica_actor = map.transarctica_actor
        map_size = {"X": raw_map.contents["rails"].px_width, "Y": raw_map.contents["rails"].px_height}
        if map_size["X"] < director.window.width:  # small map support
            padding_x = (director.window.width - map_size["X"]) / -2
        else:
            padding_x = (transarctica_actor.transarctica.current_position["X"] + 0.5) * self.tw / 2
        if map_size["Y"] < director.window.height:  # small map support
            padding_y = (director.window.height - map_size["Y"]) / -2
        else:
            padding_y = (transarctica_actor.transarctica.current_position["Y"] + 0.5) * self.tw / 2
        return padding_x, padding_y

    def get_tile_type(self, x, y):
        """returns the type of the selected tile"""
        return self.get("display_worldmap_mapscroll").get("rails").cells[x][y].tile.id - 1
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
        #    self.get("display_worldmap_mapscroll").find_engine()
        if self.get("display_worldmap_engine").visible or self.get("display_worldmap_cnc").visible or self.get("display_worldmap_quarters").visible: 
             self.ambient.volume=0.15* self.config.sound_switch
        else:
             self.ambient.volume=0.3* self.config.sound_switch
        if self.get("display_worldmap_engine").visible: 
            self.move_sound="piston_"
        else:
            self.move_sound="speed_"


