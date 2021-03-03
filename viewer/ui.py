# -*- coding: utf-8 -*-
from . import SceneCity, Gallery, DisplayTitle, SceneWorldMap, SceneCombat
from .scene_mainmenu import SceneMainMenu
from .scene_event import SceneEvent
from cocos.director import director
from cocos.scene import Scene
from cocos.scenes import RotoZoomTransition, FadeTransition
from controller import events
from model import Config
from .sound_layer import SoundLayer
import random


class UserInterface(object):
    """to start the visual part of the program"""
    def __init__(self, core):
        director.init(width=Config.window_width, height=Config.window_height)
        director.core = core
        self.gallery = Gallery()
        self.scenes = {}
        self.raw_map = None
        events.push_handlers(city=self.show_city,
                             show_event=self.show_event,
                             show_train_display=self.show_train_display,
                             minimap=self.show_minimap,
                             mainmenu=self.show_mainmenu,
                             return_to_map=self.show_worldmap,
                             show_worldmap=self.show_worldmap,
                             show_combat=self.show_combat,
                             shovel=self.do_shovel,
                             speedregulator=self.set_speedregulator,
                             commerce_switch_trade_dump=self.do_commerce_switch_trade_dump,
                             service_switch_wagons=self.do_service_switch_wagons,
                             service_repair_wagons=self.do_service_repair_wagons,
                             show_city_display=self.show_city_display,
                             wagon_select=self.do_wagon_select,
                             item_buy=self.do_item_buy,
                             item_sell=self.do_item_sell,
                             wagon_service=self.do_wagon_service,
                             scroll_minitrain=self.scroll_minitrain,
                             menu_adjutant=self.menu_adjutant,
                             close_inventory=self.close_inventory,
                             build_bridge=self.build_bridge, 
                             coal_mining=self.coal_mining, 
                             mammoth_hunt=self.mammoth_hunt, 
                             do_save=self.do_save,
                             switch_direction=self.switch_direction,
                             switch_break=self.switch_break,
                             find_engine=self.find_engine,
                             menu_xo=self.menu_xo,
                             tavern_talk=self.tavern_talk)

    def show_train_display(self, display_to_show):
        self.scenes["worldmap"].change_displays(display_to_show)

    def do_shovel(self,coal_type):
        director.core.query_mover("Transarctica").do_shovel(coal_type)

    def set_speedregulator(self):
        button_speedregulator=self.scenes["worldmap"].get("display_worldmap_engine").get("button_speedregulator")
        Speed_Regulator = min(100,max(0,(button_speedregulator.pressed_x - button_speedregulator.x - button_speedregulator.width*0.1) / (button_speedregulator.width*0.8)))
        director.core.query_mover("Transarctica").Speed_Regulator = Speed_Regulator*100
        self.scenes["worldmap"].get("display_worldmap_engine").move_speedregulator(Speed_Regulator)

    def show_minimap(self):
        if self.scenes["worldmap"].MapInZoom:
            self.scenes["worldmap"].get("display_worldmap_mapscroll")._set_scale(0.15)
        else:
            self.scenes["worldmap"].get("display_worldmap_mapscroll")._set_scale(1)
        self.scenes["worldmap"].MapInZoom = not(self.scenes["worldmap"].MapInZoom)

    def show_city(self, city_coordinates):
        """shows a city that is at tile X,y"""
        city = Config.conf_cities_by_tile[city_coordinates].name
        director.core.query_mover("Transarctica").in_city = city
        if city not in self.scenes:
           self.scenes[city] = SceneCity(Config.conf_cities_by_tile[city_coordinates])
        self.scenes["worldmap"].sound_off()
        director.replace(self.scenes[city])
        self.scenes[city].reset_displays()
        if Config.conf_cities_by_tile[city_coordinates].type != "service":
            self.show_city_display("display_city_generic")

    def show_event(self, event_type):
        if "scene_event" not in self.scenes:
           self.scenes["scene_event"] = SceneEvent()
        self.scenes["worldmap"].sound_off()
        director.replace(self.scenes["scene_event"])
        self.scenes["scene_event"].change_displays(event_type)

    def show_city_display(self, display_to_show): 
        self.scenes[director.core.query_mover("Transarctica").in_city].change_displays(display_to_show)
  
    def do_commerce_switch_trade_dump(self):
        display=self.scenes[director.core.query_mover("Transarctica").in_city].get(self.scenes[director.core.query_mover("Transarctica").in_city].active_display)
        display.switch_trade_dump()

    def do_service_switch_wagons(self):
        display=self.scenes[director.core.query_mover("Transarctica").in_city].get(self.scenes[director.core.query_mover("Transarctica").in_city].active_display)
        display.set_service_mode("S")

    def do_service_repair_wagons(self):
        display=self.scenes[director.core.query_mover("Transarctica").in_city].get(self.scenes[director.core.query_mover("Transarctica").in_city].active_display)
        display.set_service_mode("R")

    def scroll_minitrain(self):
        if director.core.sender=="button_arrow_left":
            self.scenes["worldmap"].get("display_worldmap_minitrain").x=self.scenes["worldmap"].get("display_worldmap_minitrain").x+40
        if director.core.sender=="button_arrow_right":
            self.scenes["worldmap"].get("display_worldmap_minitrain").x=self.scenes["worldmap"].get("display_worldmap_minitrain").x-40

    def do_wagon_select(self):
        display=self.scenes[director.core.query_mover("Transarctica").in_city].get("display_city_special")
        tag=display.get(director.core.sender).tag
        display.display_wagon_info(tag)

    def do_item_buy(self):
        display=self.scenes[director.core.query_mover("Transarctica").in_city].get(self.scenes[director.core.query_mover("Transarctica").in_city].active_display)
        display.do_transaction("buy",display.get(director.core.sender).tag)

    def do_item_sell(self):
        display=self.scenes[director.core.query_mover("Transarctica").in_city].get(self.scenes[director.core.query_mover("Transarctica").in_city].active_display)
        display.do_transaction("sell",display.get(director.core.sender).tag)

    def do_wagon_service(self):
        display=self.scenes[director.core.query_mover("Transarctica").in_city].get(self.scenes[director.core.query_mover("Transarctica").in_city].active_display)
        display.do_transaction("NA",display.get(director.core.sender).tag)

    def show_worldmap(self, worldmap=None):
        """
        switches to world map scene
        :param worldmap: str, absolute path to world map file
        """
        if worldmap:
            self.scenes["worldmap"] = SceneWorldMap(worldmap)
        director.core.switch_intro_music(False)
        try:
            self.scenes["scene_event"].active_display="NA"
        except:
            A=1
        self.scenes["worldmap"].sound_on()
        director.replace(self.scenes["worldmap"])
        self.find_engine()

    def show_combat(self, worldmap=None):
        """
        switches to world map scene
        :param worldmap: str, absolute path to world map file
        """
        if "combat" not in self.scenes:
            self.scenes["combat"] = SceneCombat()
        director.core.switch_intro_music(False)
        director.replace(self.scenes["combat"])



    def show_title_screen(self):
        """return to title"""
        if "title" not in self.scenes:
            title_screen = DisplayTitle()
            self.scenes["title"] = Scene(title_screen)
            director.run(self.scenes["title"])
        else:
            director.replace(RotoZoomTransition(self.scenes["title"], duration=2))

    def show_mainmenu(self):
        """shows the main menu"""
        self.scenes["mainmenu"] = SceneMainMenu()
        director.replace(FadeTransition(self.scenes["mainmenu"], duration=2))
#        director.replace(self.scenes["mainmenu"])
    
    def menu_adjutant(self):
        self.scenes["worldmap"].get("display_worldmap_quarters").menu_adjutant()

    def close_inventory(self):
        self.scenes["worldmap"].get("display_worldmap_quarters").close_inventory()

    def build_bridge(self):
        self.scenes["scene_event"].get("display_event_build_bridge").build_bridge(self.scenes["worldmap"].get("display_worldmap_mapscroll"))
        self.show_worldmap()

    def coal_mining(self):
        self.scenes["scene_event"].get("display_event_coal_mine").do_coal_mining()

    def mammoth_hunt(self):
        self.scenes["scene_event"].get("display_event_mammoth_herd").do_mammoth_hunt()

    def do_save(self):
        director.core.save_game()

    def switch_direction(self):
        director.core.query_mover("Transarctica").is_in_reverse = not(director.core.query_mover("Transarctica").is_in_reverse)

    def switch_break(self):
        director.core.query_mover("Transarctica").is_break_released = not(director.core.query_mover("Transarctica").is_break_released)

    def find_engine(self):
        self.scenes["worldmap"].get("display_worldmap_mapscroll").find_engine()

    def menu_xo(self):
        self.scenes["worldmap"].get("display_worldmap_cnc").menu_xo()

    def tavern_talk(self):
        self.scenes[director.core.query_mover("Transarctica").in_city].get("display_city_tavern").tavern_talk()