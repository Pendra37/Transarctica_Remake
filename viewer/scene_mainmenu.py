# -*- coding: utf-8 -*-
from .display_mainmenu import DisplayMainMenu
from controller import events
from cocos.director import director
from cocos.scene import Scene
from cocos.text import Label


class SceneMainMenu(Scene):
    """loads the main menu scene"""
    def __init__(self):
        """initializer"""
        Scene.__init__(self)
        self.add(DisplayMainMenu(), z=1, name="display_mainmenu")
        events.push_handlers(switch_sound_switch=self.switch_sound_switch)

    def switch_sound_switch(self):
        self.get("display_mainmenu").switch_sound()
                             