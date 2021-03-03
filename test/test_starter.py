# -*- coding: utf-8 -*-
from controller.events import events
from unittest import TestCase


class TestStarter(TestCase):
    def test_start_game(self):
        self.is_event_perceived = False
        events.push_handlers(start_game=self.start_game)
        events.emit_start_game()
        self.assertEqual(self.is_event_perceived, True)

    def start_game(self):
        self.is_event_perceived = True
