# -*- coding: utf-8 -*-
from .gallery import Gallery
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from model import Config
from math import trunc
from cocos.layer import ColorLayer

class DisplayWorldmapMiniTrain(Layer):
    """dashboard of the HUD"""
    display_pos_size = {"display_worldmap_minitrain": {"X": 0, "Y": 0.183, "W":1, "H":0.0852}}
    button_positions = {"button_arrow_left": {"X": 0.0, "Y": 0},
                        "button_arrow_right": {"X": 0.986, "Y": 0}}

    def __init__(self):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self.transarctica = director.core.query_mover("Transarctica")
        self._load_background()

    def refresh_labels(self):
        if self.transarctica.update_minitrain:
            xx=self.optimal_width*0.985
            for sp in self.get_children():
                self.remove(sp)
            white_base = ColorLayer( 235,200,130,255, width=self.optimal_width*6, height=self.optimal_height+15)
            white_base.x = self.left_margin-(self.optimal_width*3) 
            white_base.y = self.bottom_margin 
            self.add(white_base)
            for wg in self.transarctica.train_layout:
                train = Sprite(self.gallery.content["wagon"][self.config.conf_wagons[self.transarctica.train_layout[wg]].display_image+"_tr"])
                train.image_anchor = 0, 0
                train.scale = self.optimal_scale*0.40
                xx=xx-train.width
                train.x = xx
                train.y = self.bottom_margin+10
                #damage_base = ColorLayer( 85*int(self.config.conf_wagons[self.transarctica.train_layout[wg]].damage),45,45,45*int(self.config.conf_wagons[self.transarctica.train_layout[wg]].damage), width=train.width, height=train.height)
                self.add(train)
                if int(self.config.conf_wagons[self.transarctica.train_layout[wg]].damage)>0:
                    damage_base = ColorLayer( 255,0,0,255, width=trunc((train.width/4)*(4-int(self.config.conf_wagons[self.transarctica.train_layout[wg]].damage))), height=train.height//10)
                    damage_base.x = train.x
                    damage_base.y = train.y+damage_base.height*9
                    self.add(damage_base)
            self.transarctica.update_minitrain=False

    def _load_background(self):
        background = Sprite(self.gallery.content["display"]["worldmap_minitrain"])
        self.optimal_scale=(self.config.window_width * self.display_pos_size["display_worldmap_minitrain"]["W"]) / background.width
        background.image_anchor = 0, 0
        background.scale = self.optimal_scale
        background.x = self.config.window_width * self.display_pos_size["display_worldmap_minitrain"]["X"]
        background.y = self.config.window_height * self.display_pos_size["display_worldmap_minitrain"]["Y"]
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        #self.add(background)
        white_base = ColorLayer( 255,255,255,255, width=background.width*6, height=background.height+10)
        white_base.x = background.x-(background.width*3) 
        white_base.y = background.y+self.bottom_margin 
        self.add(white_base)
       
