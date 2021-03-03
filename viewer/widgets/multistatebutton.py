# -*- coding: utf-8 -*-
from . import Button


class MultiStateButton(Button):
    """
    Works like a button that changes state (sprite and event) after each click.
    States are cycled forward with left click and backwards with right click if
    backward cycling is enabled.
    """
    def __init__(self, states, scale=1, current_state=0,
                 backward_cycle_enabled=False, down_scale=0.9):
        """
        initializer
        :param states: list of button states
        :param scale: overall scale of the dashboard
        :param current_state: the state the button should be shown first
        :param backward_cycle_enabled: enables / disables right click
        """
        Button.__init__(self, states[current_state], "Multistate", 0, scale, down_scale)
        self.backward_cycle_enabled = backward_cycle_enabled
        self.states = states
        self.current_state = current_state

    @property
    def valid_mouse_buttons(self):
        if self.backward_cycle_enabled:
            return [1, 3]
        else:
            return [1]

    def _action(self, button):
        if button in self.valid_mouse_buttons:
            self.event()
#            if button == 1:
#                self._update_state(1)
#            elif button == 3 and self.backward_cycle_enabled:
#                self._update_state(-1)

    def _update_state(self, updater):
        self.current_state += updater
        self.current_state %= len(self.states)
        self._update_sprite()

    def _reset_state(self):
        self.current_state = 0
        self._update_sprite()