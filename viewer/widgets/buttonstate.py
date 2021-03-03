# -*- coding: utf-8 -*-
__author__ = 'Bárdos Dávid'


class ButtonState(object):
    """represents a state of a multistate button"""
    def __init__(self, sprite, event):
        """initializer"""
        self.event = event
        self.sprite = sprite
