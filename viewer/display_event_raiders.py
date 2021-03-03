# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from controller import events


class DisplayEvent(Layer):
    """shows a background image of the event"""
    def __init__(self, wallpaper_image):
        """initializer"""
        Layer.__init__(self)
        self.is_event_handler = True
        wallpaper = Sprite(wallpaper_image, (director.window.width/2, director.window.height/2))
        self.add(wallpaper)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 1:
            events.emit_return_to_map()
