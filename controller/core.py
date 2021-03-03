# -*- coding: utf-8 -*-
from . import events, XMLParser
from model import Config, Game
from pyglet.media import load
from pyglet.media import Player, SourceGroup


class Core(object):
    """central business logic of the game"""
    def __init__(self):
        """initializer"""
        self.game = None
        self.config = Config()
        self.sender = ""
        self.timestamp = 0
        self.TSP = 0
        # event handlers
        events.push_handlers(start_game=self.start_game,
                             sound_switch=self.sound_switch,
                             quick_battle=self.quick_battle,
                             modify_speed=self._change_time)
        self.intromusic = Player()
        source = load("music/music_title.wav")
        self.intromusic.queue(source)
        self.intromusic.volume=0.4 * self.config.sound_switch

    def tick_time(self, timestamp):
        self.timestamp=timestamp

    def _change_time(self, speed_modifier):
        """
        Changes time according to the request.
        """
        self.config.change_time_speed(speed_modifier)
        events.emit_speed_was_modified()

    def start_game(self,action):
        """event handler for starting the game"""
        self.game_name = "original64"  # "demo"  # TODO it should be gotten as an argument
        self.game = Game(self.game_name)
        XMLParser.load_cities(self.game_name)
        XMLParser.load_wagons(self.game_name)
        XMLParser.load_items(self.game_name)
        XMLParser.load_lang_file(self.game_name, "EN")
        self.query_mover("Transarctica").init_train()
        if action=="L":
            XMLParser.load_game(self.game_name, "Transarctica", self.query_mover("Transarctica"))  
            self.query_mover("Transarctica").game_loaded(self.config.loaded_objects["Transarctica"])
            for id in range(self.config.vutrain_count):
                self.query_mover("VUTrain"+str(id)).game_loaded(self.config.loaded_objects["VUTrain"+str(id)])
            for id in range(self.config.roamer_count):
                self.query_mover("Roamer"+str(id)).game_loaded(self.config.loaded_objects["Roamer"+str(id)])
        else:
            for id in range(self.config.vutrain_count):
                self.query_mover("VUTrain"+str(id)).respawn_timestamp+=self.config.start_timestamp

        self.query_mover("Transarctica").init_assets()
        events.emit_show_worldmap(self.game.map_file)

    def quick_battle(self):
        print("No boom today. Boom tomorrow. There's always a boom tomorrow.")
        events.emit_show_combat()

    def sound_switch(self):
        if self.config.sound_switch==1:
            self.config.sound_switch=0
        else:
            self.config.sound_switch=1
        self.intromusic.volume=0.4 * self.config.sound_switch


    def query_mover(self, actor_name):
        return self.game.query_mover(actor_name)

    def switch_intro_music(self, on_off):
        if on_off:
            self.intromusic.play()
        else:
            self.intromusic.pause()

    def save_game(self):
        XMLParser.save_game(self.game_name, "Transarctica", self.query_mover("Transarctica"))
        #XMLParser.save_game(self.game_name, "VUTrain0", self.query_mover("VUTrain0"))
        #XMLParser.save_game(self.game_name, "Common", self.query_mover("VUTrain0"))
