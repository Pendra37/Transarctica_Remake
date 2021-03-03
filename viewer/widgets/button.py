# -*- coding: utf-8 -*-
from . import Frame
from cocos.director import director

class Button(Frame):
    """single state button"""
    def __init__(self, state, sender, tag, scale, down_scale):
        """
        initializer
        :param state: ButtonState object
        :param scale: overall scale of the dashboard
        """
        Frame.__init__(self, side="manual")
        self.is_event_handler = True
        self.states = [state]
        self.current_state = 0
        self.original_scale = scale
        self.mouse_over_scale = scale * down_scale
        self.is_downscaled = False
        self._update_sprite()
        self.pressed_x = 0
        self.pressed_y = 0
        self.sender=sender
        self.tag=tag

    @property
    def valid_mouse_buttons(self):
        return [1]

    def _update_sprite(self):
        self.sprite.scale = self.original_scale
        self.sprite.position = self.sprite.width/2, self.sprite.height/2
        if len(self.children) > 1:
            self.children[1] = (0, self.sprite)
        else:
            self.add(self.sprite)

    def _change_sprite(self,img):
        self.sprite.image=img

    @property
    def event(self):
        return self.states[self.current_state].event
       
    @property
    def sprite(self):
        return self.states[self.current_state].sprite

    def on_mouse_press(self, x, y, button, modifiers):
        if button in self.valid_mouse_buttons and self._is_pressed((x, y)):
            self.pressed_x = x
            self.pressed_y = y
            if not self.is_downscaled:
                self._downscale()

    def _is_pressed(self, x_y):
        local_point = self.point_to_local(x_y)
        x_in_button = 0 < local_point.x < self.width
        y_in_button = 0 < local_point.y < self.height
        return x_in_button and y_in_button

    def _downscale(self):
        self.sprite.scale = self.mouse_over_scale
        self.is_downscaled = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button in self.valid_mouse_buttons:
            if self.is_downscaled:
                self._upscale()
            if self.event and self._is_pressed((x, y)):
                self._action(button)

    def _upscale(self):
        self.sprite.scale = self.original_scale
        self.is_downscaled = False

    def _action(self, button):
        try:
            director.core.sender=self.sender
        except:
            a=1        
        self.event()

       