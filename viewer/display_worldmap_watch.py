# -*- coding: utf-8 -*-
from . import Gallery
from .widgets import Frame
from cocos.director import director
from cocos.actions.interval_actions import RotateBy, RotateTo
from cocos.sprite import Sprite
from controller import events, ResolutionScaler
from math import sqrt
from model import Config
from cocos.text import Label


class DisplayWorldmapWatch(Frame):
    """watch object that shows speed and time"""
    button_positions = {"label_day_ind": {"X": 0.05, "Y": -0.2, "fsize": 13}}

    def __init__(self, start_timestamp):
        """initializer"""
        Frame.__init__(self, side="manual")
        self.config = Config()
        self.gallery = Gallery()
        self.transform_anchor = 0, 0
        scaler = ResolutionScaler(director.get_window_size())
        self.scale = scaler.get_ratio()
        self.is_event_handler = True
        events.push_handlers(speed_was_modified=self.align_speed_hand)
        self.hands = {}
        self.clock_face = None
        self.create_face()
        self.label_day_ind = self._load_label_gen("label_day_ind")
        self.add(self.label_day_ind)
        self.day=float((start_timestamp//0.5)*0.5)
        self.label_day_ind.element.text = str(self.day)
        director.core.TSP=start_timestamp
        self.create_hands(start_timestamp)
        self.pre_angle=0


    def set_watch(self, start_timestamp):
        self.label_day_ind.element.text = str(self.day)
        self.refresh_hand_positions((start_timestamp-self.day)*8640)
        self.move_hands_by_angle((start_timestamp-self.day)*8640)

    def align_speed_hand(self):
        """sets speed hand to show the current speed"""
        base_angle = 360/len(self.config.time_speed_list)
        multiplier = sorted(self.config.time_speed_list).index(self.config.time_speed)
        rotation = RotateTo(base_angle*multiplier, 0)
        self.hands["worldmap_watch_speed_hand"].do(rotation)
    
    def create_face(self):
        """creates clock face"""
        self.clock_face = Sprite(self.gallery.content["display"]["worldmap_watch"])
        self.add(self.clock_face)
        self.clock_face.position = self.clock_face.width/2, self.clock_face.height/2
        self.left_margin = self.clock_face.x
        self.bottom_margin = self.clock_face.y
        self.optimal_width = self.clock_face.width
        self.optimal_height = self.clock_face.height
        self.optimal_scale = 1 

    def create_hands(self, start_timestamp):
        """load and align hands"""
        for hand in ["worldmap_watch_time_hand", "worldmap_watch_hour_hand", "worldmap_watch_speed_hand"]:
            self.hands[hand] = Sprite(self.gallery.content["display"][hand])
            self.hands[hand].image_anchor_y = 0
            self.hands[hand].position = self.clock_face.width/2, self.clock_face.height/2
            if "worldmap_watch_hour_hand" == hand:
                self.hands[hand].rotation = (start_timestamp-self.day)*720
            if "worldmap_watch_time_hand" == hand:
                self.hands[hand].rotation = (((start_timestamp-self.day)%0.041667)/0.041667)*360
            self.add(self.hands[hand])
        self.align_speed_hand()

    def is_within_watch(self, click_x, click_y):
        """
        :argument x: pixel coordinate
        :argument y: pixel coordinate
        :returns: True if click was on the clock
        """
        x_distance = click_x - (self.clock_face.x * self.scale)
        y_distance = click_y - (self.clock_face.y * self.scale)
        distance_from_center = sqrt((x_distance**2)+(y_distance**2))
        radius = self.clock_face.width / 2 * self.scale
        return distance_from_center < radius

    def on_mouse_press(self, x, y, buttons, modifiers):
        """manipulates time"""
        if not self.is_within_watch(x, y):
            return
        new_speed = 0
        if buttons == 1:
            new_speed = 1
        elif buttons == 4:
            new_speed = -1
        if new_speed:
            events.emit_modify_speed(new_speed)

    def refresh_hand_positions(self, dt):
        angle_to_move = self.get_angle_from_delta_time(dt)
        self.move_hands_by_angle(angle_to_move)
        if self.pre_angle>self.hands["worldmap_watch_hour_hand"].rotation:
            self.day=self.day+0.5
            self.label_day_ind.element.text = str(self.day)
        director.core.tick_time(self.day+self.hands["worldmap_watch_hour_hand"].rotation/720)
        self.pre_angle=self.hands["worldmap_watch_hour_hand"].rotation

    def get_angle_from_delta_time(self, delta_time):
        """
        :param delta_time: time spent since the last render
        :return: angle the hands should be moved by
        """
        time_multiplier = self.config.simulation_speed * self.config.time_speed
        delta_ingame_time = delta_time * time_multiplier
        angle_to_move = 0.1 * delta_ingame_time  # 1 minute is 6° on the clock
        return angle_to_move

    def move_hands_by_angle(self, angle_to_move):
        """reposition hands
        :param angle_to_move: degrees
        """
        self.hands["worldmap_watch_time_hand"].do(RotateBy(angle_to_move, 0))
        self.hands["worldmap_watch_hour_hand"].do(RotateBy(angle_to_move / 12, 0))

    def _load_label_gen(self, obj_name):
        x = self.optimal_width * self.button_positions[obj_name]["X"] + self.left_margin
        y = self.optimal_height * self.button_positions[obj_name]["Y"] + self.bottom_margin
        fsize = round(self.optimal_scale * self.button_positions[obj_name]["fsize"])
        return Label("---", (x, y), color=(0,0,0,255), font_name="Arial", bold=True, font_size=fsize, anchor_x="right", anchor_y="center")
