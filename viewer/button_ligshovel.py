# -*- coding: utf-8 -*-
from cocos.sprite import Sprite
from controller import events
from .gallery import Gallery
from .widgets import ButtonState, Button, MultiStateButton

__author__ = 'Bárdos Dávid'


class ButtonLigShovel(MultiStateButton):
    """button to shovel in some lignite with 2 speed settings """
    def __init__(self, scale=1):
        """initializer"""
        gallery = Gallery()
        sprite_ligshovel_stop = Sprite(gallery["button"]["ligshovel_stop"])
        sprite_ligshovel_slow = Sprite(gallery["button"]["ligshovel_slow"])
        sprite_ligshovel_fast = Sprite(gallery["button"]["ligshovel_fast"])
        ligshovel_stop = ButtonState(sprite=sprite_ligshovel_stop, event=events.emit_do_ligshovel)
        ligshovel_slow = ButtonState(sprite=sprite_ligshovel_slow, event=events.emit_do_ligshovel)
        ligshovel_fast = ButtonState(sprite=sprite_ligshovel_fast, event=events.emit_do_ligshovel)
        states = [ligshovel_stop, ligshovel_slow, ligshovel_fast]
        scale=scale
        MultiStateButton.__init__(self, states=states, scale=scale, down_scale=1)
        self.position = self.width / 2, self.height / 2
