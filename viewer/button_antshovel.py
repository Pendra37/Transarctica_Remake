# -*- coding: utf-8 -*-
from cocos.sprite import Sprite
from controller import events
from .gallery import Gallery
from .widgets import ButtonState, Button, MultiStateButton

__author__ = 'Bárdos Dávid'


class ButtonAntShovel(MultiStateButton):
    """button to shovel in some anthracit with 2 speed settings """
    def __init__(self, scale=1):
        """initializer"""
        gallery = Gallery()
        sprite_antshovel_stop = Sprite(gallery["button"]["antshovel_stop"])
        sprite_antshovel_slow = Sprite(gallery["button"]["antshovel_slow"])
        sprite_antshovel_fast = Sprite(gallery["button"]["antshovel_fast"])
        antshovel_stop = ButtonState(sprite=sprite_antshovel_stop, event=events.emit_do_antshovel)
        antshovel_slow = ButtonState(sprite=sprite_antshovel_slow, event=events.emit_do_antshovel)
        antshovel_fast = ButtonState(sprite=sprite_antshovel_fast, event=events.emit_do_antshovel)
        states = [antshovel_stop, antshovel_slow, antshovel_fast]
        scale=scale
        MultiStateButton.__init__(self, states=states, scale=scale, down_scale=1)
        self.position = self.width / 2, self.height / 2
