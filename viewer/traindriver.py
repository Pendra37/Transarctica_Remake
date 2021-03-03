# -*- coding: utf-8 -*-
from cocos.actions.move_actions import Driver


class TrainDriver(Driver):
    """slightly modified Driver for the train"""
    def step(self, dt):
        """avoids passing target node"""
        accel = getattr(self.target, 'acceleration', 0)
        speed = self.target.get_speed()#*0.85
        max_forward = getattr(self.target, 'max_forward_speed', None)
        max_reverse = getattr(self.target, 'max_reverse_speed', None)
        if accel:
            speed += dt * accel
            if max_forward is not None and self.target.speed > max_forward:
                speed = max_forward
            if max_reverse is not None and self.target.speed < max_reverse:
                speed = max_reverse
        s = dt * speed
        x, y = self.target.position
        delta_x, delta_y = self.target.convert_progression_to_direction_vectors(s)
        next_node_distance = self.target.get_target_node_distance()
        if s >= next_node_distance:
            self.target.position = self.target.target_node
        else:
            self.target.position = (x + delta_x, y + delta_y)
        #print(str(self.target.position))

    def step_transarctica(self, dt):
        accel = getattr(self.target, 'acceleration', 0)
        speed = self.target.get_speed()#*0.85
        max_forward = getattr(self.target, 'max_forward_speed', None)
        max_reverse = getattr(self.target, 'max_reverse_speed', None)
        if accel:
            speed += dt * accel
            if max_forward is not None and self.target.speed > max_forward:
                speed = max_forward
            if max_reverse is not None and self.target.speed < max_reverse:
                speed = max_reverse
        step = dt * speed
        x, y = self.target.position
        delta_x, delta_y = self.target.convert_progression_to_direction_vectors(step)
        if self.target.next_turn_at!=(-1,-1):
            if self.target.on_tile in ["bumper", "city_bumper"]: 
                if 32 < self.target.get_distance_between_points(self.target.position, self.target.tile_entry_point):
                    x, y = self.target.next_turn_at
                    delta_x = 0
                    delta_y = 0
                    #self.target.transarctica.speed=0
                    self.target.stop()
                    self.target.start()
                    self.target.transarctica.is_in_reverse = not(self.target.transarctica.is_in_reverse)
                    if self.target.on_tile=="city_bumper":
                        self.target.city_bumper_hit()
            #elif self.target.on_tile in ["switch"]: 
            #    if step >= self.target.get_distance_between_points(self.target.position, self.target.next_turn_at):
            #        step -= self.target.get_distance_between_points(self.target.position, self.target.next_turn_at)
            #        x, y = self.target.next_turn_at
            #        self.target.transarctica.direction=self.target.leaving_toward
            #        delta_x, delta_y = self.target.convert_progression_to_direction_vectors(step)
            elif self.target.on_tile in ["cross", "normal", "switch"]: 
                if step >= self.target.get_distance_between_points(self.target.position, self.target.next_turn_at):
                    step -= self.target.get_distance_between_points(self.target.position, self.target.next_turn_at)
                    x, y = self.target.next_turn_at
                    self.target.transarctica.direction=self.target.leaving_toward
                    delta_x, delta_y = self.target.convert_progression_to_direction_vectors(step)
                    self.target.next_turn_at=(-1,-1)
        self.target.position = (x + delta_x, y + delta_y)


    def step_vutrain(self, dt):
        accel = getattr(self.target, 'acceleration', 0)
        speed = self.target.get_speed()#*0.85
        max_forward = getattr(self.target, 'max_forward_speed', None)
        max_reverse = getattr(self.target, 'max_reverse_speed', None)
        if accel:
            speed += dt * accel
            if max_forward is not None and self.target.speed > max_forward:
                speed = max_forward
            if max_reverse is not None and self.target.speed < max_reverse:
                speed = max_reverse
        step = dt * speed
        x, y = self.target.position
        delta_x, delta_y = self.target.convert_progression_to_direction_vectors(step)
        if self.target.next_turn_at!=(-1,-1):
            if self.target.on_tile in ["bumper", "city_bumper"]: 
                if 32 < self.target.get_distance_between_points(self.target.position, self.target.tile_entry_point):
                    x, y = self.target.next_turn_at
                    delta_x = 0
                    delta_y = 0
                    self.target.vutrain.speed=0
                    self.target.vutrain.is_in_reverse = not(self.target.vutrain.is_in_reverse)
                    if self.target.on_tile=="city_bumper":
                        self.target.city_bumper_hit()
            #elif self.target.on_tile in ["switch"]: 
            #    if step >= self.target.get_distance_between_points(self.target.position, self.target.next_turn_at):
            #        step -= self.target.get_distance_between_points(self.target.position, self.target.next_turn_at)
            #        x, y = self.target.next_turn_at
            #        self.target.vutrain.direction=self.target.leaving_toward
            #        delta_x, delta_y = self.target.convert_progression_to_direction_vectors(step)
            elif self.target.on_tile in ["cross", "normal", "switch"]: 
                if step >= self.target.get_distance_between_points(self.target.position, self.target.next_turn_at):
                    step -= self.target.get_distance_between_points(self.target.position, self.target.next_turn_at)
                    x, y = self.target.next_turn_at
                    self.target.vutrain.direction=self.target.leaving_toward
                    delta_x, delta_y = self.target.convert_progression_to_direction_vectors(step)
                    self.target.next_turn_at=(-1,-1)
        self.target.position = (x + delta_x, y + delta_y)


    def step_roamer(self, dt):
        accel = getattr(self.target, 'acceleration', 0)
        speed = self.target.get_speed()#*0.85
        max_forward = getattr(self.target, 'max_forward_speed', None)
        if accel:
            speed += dt * accel
            if max_forward is not None and self.target.speed > max_forward:
                speed = max_forward
        step = dt * speed
        x, y = self.target.position
        delta_x, delta_y = self.target.convert_progression_to_direction_vectors(step)
        self.target.position = (x + delta_x, y + delta_y)
