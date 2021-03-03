# -*- coding: utf-8 -*-
from pyglet.event import EventDispatcher
from model import Config


class Events(EventDispatcher):
    """holds most important events"""
    def __init__(self):
        """initializer"""
        EventDispatcher.__init__(self)
        self.config = Config()
        events_to_register = ["switch_break", 
                              "switch_direction",
                              "city", 
                              "show_event",
                              "show_train_display",
                              "mainmenu",
                              "modify_speed", 
                              "return_to_map", 
                              "find_engine", 
                              "minimap", 
                              "shovel", 
                              "show_worldmap", 
                              "show_combat", 
                              "speed_was_modified",
                              "speedregulator",
                              "start_game", 
                              "quick_battle", 
                              "sound_switch",
                              "load_game", 
                              "commerce_switch_trade_dump", 
                              "service_switch_wagons",
                              "service_repair_wagons",
                              "show_city_display",
                              "wagon_select",
                              "wagon_buy",
                              "wagon_sell",
                              "item_buy",
                              "item_sell",
                              "wagon_service",
                              "scroll_minitrain",
                              "menu_adjutant",
                              "close_inventory",
                              "build_bridge",
                              "coal_mining",
                              "mammoth_hunt",
                              "do_save",
                              "switch_sound_switch",
                              "menu_xo",
                              "tavern_talk"]
        for event in events_to_register:
            self.register_event_type(event)

    def emit_switch_break(self):
        self.dispatch_event("switch_break")

    def emit_switch_direction(self):
        self.dispatch_event("switch_direction")

    def emit_modify_speed(self, new_speed):
        self.dispatch_event("modify_speed", new_speed)

    def emit_return_to_map(self):
        self.dispatch_event("return_to_map")

    def emit_show_city(self, city_coordinates):
        self.dispatch_event("city", city_coordinates)

    def emit_show_event(self, event_type):
        self.dispatch_event("show_event", event_type)

    def emit_find_engine(self):
        self.dispatch_event("find_engine")

    def emit_show_engine(self):
        self.dispatch_event("show_train_display","display_worldmap_engine")

    def emit_show_quarters(self):
        self.dispatch_event("show_train_display","display_worldmap_quarters")

    def emit_show_cnc(self):
        self.dispatch_event("show_train_display","display_worldmap_cnc")

    def emit_show_launcher(self):
        self.dispatch_event("show_train_display","display_launcher")

    def emit_show_minimap(self):
        self.dispatch_event("minimap")

    def emit_do_ligshovel(self):
        self.dispatch_event("shovel","Lignite")

    def emit_do_antshovel(self):
        self.dispatch_event("shovel","Anthracite")

    def emit_show_worldmap(self, worldmap):
        self.dispatch_event("show_worldmap", worldmap)

    def emit_show_mainmenu(self):
        self.dispatch_event("mainmenu")

    def emit_speed_was_modified(self):
        self.dispatch_event("speed_was_modified")

    def emit_start_game(self):
        self.dispatch_event("start_game","S")

    def emit_quick_battle(self):
        self.dispatch_event("quick_battle")

    def emit_load_game(self):
        self.dispatch_event("start_game","L")

    def emit_show_combat(self):
        self.dispatch_event("show_combat")


    def emit_sound_switch(self):
        self.dispatch_event("sound_switch")
        self.dispatch_event("switch_sound_switch")

    def emit_speedregulator(self):
        self.dispatch_event("speedregulator")

    def emit_commerce_switch_trade_dump(self):
        self.dispatch_event("commerce_switch_trade_dump")

    def emit_service_switch_wagons(self):
        self.dispatch_event("service_switch_wagons")

    def emit_service_repair_wagons(self):
        self.dispatch_event("service_repair_wagons")

    def emit_wagon_select(self):
        self.dispatch_event("wagon_select")

    def emit_wagon_buy(self):
        self.dispatch_event("wagon_buy")

    def emit_wagon_sell(self):
        self.dispatch_event("wagon_sell")

    def emit_item_buy(self):
        self.dispatch_event("item_buy")

    def emit_item_sell(self):
        self.dispatch_event("item_sell")

    def emit_wagon_service(self):
        self.dispatch_event("wagon_service")

    def emit_scroll_minitrain(self):
        self.dispatch_event("scroll_minitrain")

    def emit_show_city_barracks(self):
        self.dispatch_event("show_city_display","display_city_barracks")

    def emit_show_city_commerce(self):
        self.dispatch_event("show_city_display","display_city_commerce")

    def emit_show_city_special(self):
        self.dispatch_event("show_city_display","display_city_special")

    def emit_show_city_tavern(self):
        self.dispatch_event("show_city_display","display_city_tavern")

    def emit_show_city_generic(self):
        self.dispatch_event("show_city_display","display_city_generic")

    def emit_menu_adjutant(self):
        self.dispatch_event("menu_adjutant")

    def emit_close_inventory(self):
        self.dispatch_event("close_inventory")

    def emit_build_bridge(self):
        self.dispatch_event("build_bridge")

    def emit_coal_mining(self):
        self.dispatch_event("coal_mining")

    def emit_mammoth_hunt(self):
        self.dispatch_event("mammoth_hunt")

    def emit_save(self):
        self.dispatch_event("do_save")

    def emit_menu_xo(self):
        self.dispatch_event("menu_xo")

    def emit_tavern_talk(self):
        self.dispatch_event("tavern_talk")

events = Events()
