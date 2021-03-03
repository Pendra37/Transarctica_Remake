# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.scene import Scene
from cocos.text import Label
from model.config import Config
from .gallery import Gallery
from .display_city_generic import DisplayCityGeneric
from .display_city_commerce import DisplayCityCommerce
from .display_city_commerce_wagon import DisplayCityCommerceWagon
from .display_city_tavern import DisplayCityTavern
from .display_city_service import DisplayCityService
from .display_city_hud import DisplayCityHUD
import random

class SceneCity(Scene):
    """loads a city"""
    possible_specials={1 : "barracks", 2 : "mammoth", 3 : "slave", 4 : "wagon"}

    def __init__(self, city):
        """initializer"""
        Scene.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.city=city
        self.special=self.possible_specials[4]
        self.add_displays()
        self.next_update=director.core.timestamp+(random.randint(5,20)/10)
        self.active_display="display_city_generic"

    def add_displays(self):
        cz = 1
        self.add(DisplayCityHUD(), z=cz, name="display_city_hud")
        cz +=1
        if self.city.type != "service":
            self.add(DisplayCityGeneric(), z=cz, name="display_city_generic")
            cz +=1
            self.add(DisplayCityCommerce(self.city.supply, "commerce"), z=cz, name="display_city_commerce")
            cz +=1
            self.add(DisplayCityTavern(), z=cz, name="display_city_tavern")
            cz +=1
            self.add(DisplayCityCommerce(self.city.supply, "barracks"), z=cz, name="display_city_barracks")
            cz +=1
            if self.city.type=="commercial":
                self.special=self.possible_specials[random.randint(1,len(self.possible_specials))]
            else:
                self.special=self.city.type
            if self.special=="barracks":
                self.add(DisplayCityCommerce(self.city.supply, "barracks"), z=cz, name="display_city_special")
            if self.special=="mammoth":
                self.add(DisplayCityCommerce(self.city.supply, "mammoth"), z=cz, name="display_city_special")
            if self.special=="slave":
                self.add(DisplayCityCommerce(self.city.supply, "slave"), z=cz, name="display_city_special")
            if self.special=="wagon":
                self.add(DisplayCityCommerceWagon("wagon"), z=cz, name="display_city_special")
        else:
            self.add(DisplayCityService(), z=cz, name="display_city_generic")
            self.active_display="display_city_generic"

    def clear_displays(self):
        self.remove("display_city_hud")
        if self.city.type != "service":
            self.remove("display_city_generic")
            self.remove("display_city_commerce")
            self.remove("display_city_tavern")
            self.remove("display_city_barracks")
            self.remove("display_city_special")
        else:
            self.remove("display_city_service")
            
    def reset_displays(self):
        if self.city.type != "service":
            self.get("display_city_commerce").update_desc()
            if self.next_update<director.core.timestamp:
                self.next_update=director.core.timestamp+(random.randint(5,20)/10)
                self.clear_displays()
                self.add_displays()

    def change_displays(self, display_to_show):
        self.get("display_city_generic").set_visibility(False)
        self.get("display_city_barracks").set_visibility(False)
        self.get("display_city_commerce").set_visibility(False)
        self.get("display_city_special").set_visibility(False)
        self.get("display_city_tavern").set_visibility(False)
        self.get(display_to_show).set_visibility(True)
        self.active_display=display_to_show

