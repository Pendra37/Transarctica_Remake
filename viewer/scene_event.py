# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.scene import Scene
from cocos.text import Label
from model.config import Config
from .gallery import Gallery
from .display_city_hud import DisplayCityHUD
from .display_event_tunnel_block import DisplayEventTunnelBlock
from .display_event_bridge_monster import DisplayEventBridgeMonster
from .display_event_build_bridge import DisplayEventBuildBridge
from .display_event_train_combat import DisplayEventTrainCombat
from .display_event_nomads import DisplayEventNomads
from .display_event_mammoth_herd import DisplayEventMammothHerd
from .display_event_coal_mine import DisplayEventCoalMine
import random



class SceneEvent(Scene):
    """loads an event scene"""
    def __init__(self):
        """initializer"""
        Scene.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.add_displays()
        self.active_display="NA"

    def add_displays(self):
        cz = 1
        self.add(DisplayCityHUD(), z=cz, name="display_city_hud")
        cz += 1
        self.add(DisplayEventTunnelBlock(), z=cz, name="display_event_tunnel_block")
        cz += 1
        self.add(DisplayEventBridgeMonster(), z=cz, name="display_event_bridge_monster")
        cz += 1
        self.add(DisplayEventBuildBridge(), z=cz, name="display_event_build_bridge")
        cz += 1
        self.add(DisplayEventTrainCombat(), z=cz, name="display_event_train_combat")
        cz += 1
        self.add(DisplayEventNomads(), z=cz, name="display_event_nomads")
        cz += 1
        self.add(DisplayEventMammothHerd(), z=cz, name="display_event_mammoth_herd")
        cz += 1
        self.add(DisplayEventCoalMine(), z=cz, name="display_event_coal_mine")
          
    def change_displays(self, display_to_show):
        if self.active_display=="NA":
            self.get("display_event_tunnel_block").set_visibility(False)
            self.get("display_event_bridge_monster").set_visibility(False)
            self.get("display_event_build_bridge").set_visibility(False)
            self.get("display_event_train_combat").set_visibility(False)
            self.get("display_event_nomads").set_visibility(False)
            self.get("display_event_mammoth_herd").set_visibility(False)
            self.get("display_event_coal_mine").set_visibility(False)
            #self.get("display_city_tavern").set_visibility(False)
            self.get(display_to_show).set_visibility(True)
            self.active_display=display_to_show

