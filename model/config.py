# -*- coding: utf-8 -*-
from os.path import dirname


class Config(object):
    """
    Borg object holding all the configuration settings of the game.
    "We are all one."
    """
    __shared_state = {}
    # Application level variables
    cities = "_cities.xml"  # city database
    wagons = "_wagons.xml"  # city database
    items = "_items.xml"  # city database
    default_map = "original64"  # default map setting
    frames_per_sec = 60
    graphics_format = ["png", "jpg", "gif"]  # recognized gfx formats
    language_name_template = "lang_{}.xml"
    map_format = "tmx"
    resources = "{}/resources".format(dirname(dirname(__file__, )).replace("\\", "/"))
    scroll_speed = 3
    simulation_speed = 125  # seconds so accurate values can be set, this is the base simulation speed
    time_speed_list = [0, 1, 5, 10]
    window_height = 900-38#1080-38
    window_width = 1600-16#1920-16
    # Game level variables
    km_per_tile = 50  # tile width in kilometres
    tile_width = 64
    map_width=160
    map_height=72
    time_speed = 1

    loaded_objects = {}

    conf_cities_by_tile = {}
    conf_cities_by_name = {}
    conf_wagons = {}
    base_wagon_range = -1
    conf_storage_type = {}
    conf_items = {}
    conf_city_sup_dem_matrix = {"agri" : {"resources" : {"need" : 1, "price_mod" : 1}, "lowtech" : {"need" : 2, "price_mod" : 1}, "weapons" : {"need" : 3, "price_mod" : 3}, "hightech" : {"need" : 1, "price_mod" : 3}},
                                "resources"  : {"agri" : {"need" : 3, "price_mod" : 1}, "lowtech" : {"need" : 3, "price_mod" : 3}, "weapons" : {"need" : 2, "price_mod" : 2}, "hightech" : {"need" : 2, "price_mod" : 2}},
                                "lowtech"  : {"agri" : {"need" : 3, "price_mod" : 1}, "resources" : {"need" : 3, "price_mod" : 3}, "weapons" : {"need" : 2, "price_mod" : 2}, "hightech" : {"need" : 2, "price_mod" : 2}},
                                "weapons" : {"agri" : {"need" : 3, "price_mod" : 2}, "resources" : {"need" : 3, "price_mod" : 2}, "lowtech" : {"need" : 2, "price_mod" : 2}, "hightech" : {"need" : 2, "price_mod" : 2}},
                                "hightech" : {"agri" : {"need" : 3, "price_mod" : 3}, "resources" : {"need" : 2, "price_mod" : 1}, "lowtech" : {"need" : 3, "price_mod" : 2}, "weapons" : {"need" : 2, "price_mod" : 2}}}
    start_position = {"X": 13, "Y": 9}

    vu_start_positions = {}
    vu_start_positions[len(vu_start_positions)]={"X":   8, "Y": 31, "D":"W"}
    vu_start_positions[len(vu_start_positions)]={"X":  11, "Y": 29, "D":"S"}
    vu_start_positions[len(vu_start_positions)]={"X":  13, "Y": 31, "D":"E"}
    vu_start_positions[len(vu_start_positions)]={"X":  74, "Y": 10, "D":"W"}
    vu_start_positions[len(vu_start_positions)]={"X":  77, "Y":  8, "D":"S"}  
    vu_start_positions[len(vu_start_positions)]={"X":  78, "Y": 11, "D":"N"}
    vu_start_positions[len(vu_start_positions)]={"X": 112, "Y": 47, "D":"N"}
    vu_start_positions[len(vu_start_positions)]={"X": 112, "Y": 45, "D":"W"}
    vu_start_positions[len(vu_start_positions)]={"X": 116, "Y": 46, "D":"E"}

    vutrain_count=10

    roamer_count=20
    roamer_types = ["nomads", "mammoth_herd"]  
    coal_mine_count=10
    coal_mine = {}

    start_train=["Locomotive","Tender","Command and Control","Quarters","Barracks","Merchandise"]
    #start_train=["Locomotive","Tender","Command and Control","Quarters","Barracks","XL Merchandise", "XL Tanker", "Bio-greenhouse", "Harpoon", "Refrigerator", "Livestock"]
    start_items={"Lignite": 2000, "Anthracite": 1000, "Soldier Infantry": 10}
    start_items_values={}
    start_timestamp=1     
    boiler_cooldown_rate = 0.04
    anthracite_shovel_qty=2
    lignite_shovel_qty=2
    maximum_speed = 300
    minimum_speed = 0
    speeding_rate = 3#30 #2
    breaking_rate = -50  # not instant
    base_vis_range=3
    molemen_force = {"min":50, "max":250}
    molemen_loot = {"min":5, "max":40}
    tunnel_block_chance=0

    lang_file = {}

    sound_switch=1


    def __init__(self):
        """initializer"""
        self.__dict__ = self.__shared_state

    def change_time_speed(self, speed_modifier):
        """
        :argument speed_modifier: can be 1 or -1
        Changes the time according to the speed modifier.
        """
        if speed_modifier not in [1, -1]:
            raise ValueError("speed_modifier have to be 1 or -1.")
        current_time_index = self.time_speed_list.index(self.time_speed)
        new_time_index = (current_time_index + speed_modifier) % len(self.time_speed_list)
        self.time_speed = self.time_speed_list[new_time_index]
