# -*- coding: utf-8 -*-
from cocos.sprite import Sprite
from controller import events
from .gallery import Gallery
from .widgets import ButtonState, Button

__author__ = 'Bárdos Dávid'


class ButtonSpeedRegulator(Button):
    """button that changes the train's speed regulator"""
    def __init__(self, scale=1):
        """initializer"""
        gallery = Gallery()
        sprite = Sprite(gallery["button"]["speedregulator"])
        state = ButtonState(sprite, events.emit_speedregulator)
        Button.__init__(self, state, "button_speedregulator", 0, scale, 1)
        self.position = self.width / 2, self.height / 2
