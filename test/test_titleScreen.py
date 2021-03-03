# -*- coding: utf-8 -*-
from controller import events
from viewer import Gallery, TitleScreen
from unittest import TestCase


class TestTitleScreen(TestCase):
    def test_on_mouse_press(self):
        self.is_start_emitted = False
        events.push_handlers(start_game=self.set_start_emitted)
        t = TitleScreen()
        t.on_mouse_press(0, 0, [], {})
        self.assertTrue(self.is_start_emitted)

    def set_start_emitted(self):
        self.is_start_emitted = True
