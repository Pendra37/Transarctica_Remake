# -*- coding: utf-8 -*-
from cocos.actions import ScaleBy
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from controller import events
from . import Gallery
from model import Config
from pyglet.media import load

class SoundLayer(Layer):
    display_pos_size = {"display_title": {"X": 0, "Y": 0, "W":1, "H":1}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.schedule_interval(self.music_start, interval=7)
        self.intro_sound = load("music/sound_start.wav", streaming=False)
        self.intro_sound.play()
        self.is_event_handler = True
        background = Sprite(self.gallery.content["display"]["title"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_title"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_title"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_title"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        self.add(background)
        place_holder_image = Sprite(self.gallery.content["screen"]["title"])
        place_holder_image.position = director.window.width/2, director.window.height/2
        place_holder_image.scale=self.optimal_scale
        place_holder_image.do(ScaleBy(5.2, duration=25))
        self.add(place_holder_image)

    def on_mouse_press(self, x, y, buttons, modifiers):
        events.emit_show_mainmenu()

    def music_start(self, event):
        self.intro_music = load("music/music_title.wav", streaming=False)
        self.intro_music.play()
        self.unschedule(self.music_start)