# -*- coding: utf-8 -*-
from cocos.actions import ScaleBy, FadeOut
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from controller import events
from . import Gallery
from model import Config
from pyglet.media import load
from pyglet.media import Player, SourceGroup

class DisplayTitle(Layer):
    display_pos_size = {"display_title": {"X": 0, "Y": 0, "W":1, "H":1}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.wind = Player()
        source = load("music/sound_start.wav")
        self.wind.queue(source)
        self.wind.volume=0.3
        self.wind.play()
        self.background = Sprite(self.gallery.content["display"]["title"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_title"]["W"]) / self.background.width
        self.background.image_anchor = 0, 0
        self.background.scale = self.optimal_scale
        self.background.x = self.config.window_width * self.display_pos_size["display_title"]["X"]
        self.background.y = self.config.window_height * self.display_pos_size["display_title"]["Y"]
        self.left_margin = self.background.x
        self.bottom_margin = self.background.y
        self.optimal_width = self.background.width
        self.optimal_height = self.background.height

        place_holder_image = Sprite(self.gallery.content["screen"]["title"])
        place_holder_image.position = director.window.width/2, director.window.height/2
        #place_holder_image.scale=self.optimal_scale/30
        #place_holder_image.do(ScaleBy(45, duration=35))
        place_holder_image.scale=self.optimal_scale
        self.add(place_holder_image)
        self.background2=self.background
        self.add(self.background)
        self.add(self.background2)
        self.schedule_interval(self.intro_train_start, interval=5)
        self.schedule_interval(self.intro_music_start, interval=4)
        self.is_event_handler = True

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.wind.pause()
        self.unschedule(self.intro_music_start)
        self.unschedule(self.intro_train_start)
        events.emit_show_mainmenu()

    def intro_music_start(self, event):
        director.core.switch_intro_music(True)
        self.unschedule(self.intro_music_start)
    
    def intro_train_start(self, event):
        self.background.do(FadeOut(duration=20))
        self.unschedule(self.intro_train_start)