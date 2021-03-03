# -*- coding: utf-8 -*-
from cocos.sprite import Sprite
from controller import events
from .gallery import Gallery
from .widgets import ButtonState, Button

__author__ = 'Bárdos Dávid'


class ButtonGen(Button):
    """generic button class for simple buttons"""
    def __init__(self, pic1, pic2, sendevent, sender, tag, scale, down_scale):
        """initializer"""
        gallery = Gallery()
        sprite = Sprite(gallery[pic1][pic2])
        state = ButtonState(sprite, sendevent)
        Button.__init__(self, state, sender, tag, scale, down_scale)
        self.position = self.width / 2, self.height / 2
