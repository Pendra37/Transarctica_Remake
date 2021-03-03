# -*- coding: utf-8 -*-
from .gallery import Gallery
from cocos.director import director
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.text import Label
from controller import events
from model import Config
from cocos.menu import Menu, CENTER, MenuItem
import sys

class DisplayInteractBox(Layer):
    def __init__(self,opt,bubble_type,px,py,pscale):
        Layer.__init__(self)
        self.config = Config()
        self.gallery = Gallery()
        self._load_background(bubble_type,px,py,pscale)
        self._load_interface(opt)

    def _load_background(self,bubble_type,px,py,pscale):
        background = Sprite(self.gallery.content["text"]["bubble_"+bubble_type])
        background.scale = pscale
        background.image_anchor = 0, 0
        background.x = px
        background.y = py
        self.left_margin = background.x
        self.bottom_margin = background.y
        self.optimal_width = background.width
        self.optimal_height = background.height
        #self.add(background)

    def _load_interface(self,opt):
        if len(opt)>0:
            IO = Interact_Options(opt)
            IO.x=self.left_margin-self.config.window_width//2+self.optimal_width//2
            IO.y=self.bottom_margin-self.config.window_height//2+self.optimal_height//2
            self.add(IO)


class Interact_Options(Menu):
    def __init__(self,opt):
        super(Interact_Options, self).__init__("")
        self.transarctica = director.core.query_mover("Transarctica")
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        menu_items = []
        self.menu_params = {}
        for id in range(len(opt)):
            func=getattr(self, "option_"+str(id))
            if callable(func):
                menu_items.append(MenuItem(opt[str(id)]["text"],func))
                self.menu_params[str(id)]={"param" : opt[str(id)]["param"] }
            else:
                break


        self.font_item = {
            'font_name': 'Arial',
            'font_size': 16,
            'bold': False,
            'italic': False,
            'anchor_y': 'bottom',
            'anchor_x': 'left',
            'color': (255, 255, 255, 255),
            'dpi': 96,
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 16,
            'bold': True,
            'italic': False,
            'anchor_y': 'bottom',
            'anchor_x': 'left',
            'color': (64, 64, 255, 255),
            'dpi': 96,
        }

        self.create_menu(menu_items)

    def option_0(self):
        self.interact_events(self.menu_params["0"]["param"])

    def option_1(self):
        self.interact_events(self.menu_params["1"]["param"])

    def option_2(self):
        self.interact_events(self.menu_params["2"]["param"])

    def option_3(self):
        self.interact_events(self.menu_params["3"]["param"])

    def option_4(self):
        self.interact_events(self.menu_params["4"]["param"])

    def interact_events(self, param):
        self.parent.parent.clear_text()
        if param=="prospect":
            cell = self.transarctica.map.get("rails").cells[self.transarctica.current_position["X"]][self.transarctica.current_position["Y"]]
            if "coal_mine" in cell.properties:
                if cell.properties["coal_mine"]>0: 
                    self.transarctica.last_event_position["X"]=self.transarctica.current_position["X"]
                    self.transarctica.last_event_position["Y"]=self.transarctica.current_position["Y"]
                    events.emit_show_event("display_event_coal_mine")
                else:
                    self.parent.parent.get("label_line_1").element.text="The coal mine in the area has been depleted."
            else:
                self.parent.parent.get("label_line_1").element.text="The prospector teams found no coal in the area."

        elif param=="mine":
            self.parent.parent.get("label_line_1").element.text="No explosives available."
        elif param=="discuss_xo":
            self.parent.parent.discuss_with_xo()
        elif param=="discuss_adjutant":
            self.parent.parent.discuss_with_adjutant()
        elif param=="inventory":
            self.parent.parent.show_inventory()
        elif param=="end":
            self.parent.parent.remove_interact()
    
    def on_quit(self):
        exit()

