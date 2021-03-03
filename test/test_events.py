# -*- coding: utf-8 -*-
from controller import events
from unittest import TestCase


class TestEvents(TestCase):
    current_event_emitted = False

    def react_to_event(self, *args, **kwargs):
        self.current_event_emitted = True
        self.args = args
        self.kwargs = kwargs

    def test_emit_return_to_map(self):
        self.current_event_emitted = False
        events.push_handlers(return_to_map=self.react_to_event)
        events.emit_return_to_map()
        self.assertTrue(self.current_event_emitted)

    def test_emit_show_city(self):
        self.current_event_emitted = False
        events.push_handlers(city=self.react_to_event)
        events.emit_show_city("dummy_city_name")
        self.assertTrue(self.current_event_emitted)

    def test_emit_show_world_map(self):
        self.current_event_emitted = False
        events.push_handlers(show_world_map=self.react_to_event)
        events.emit_show_world_map("dummy_map")
        self.assertTrue(self.current_event_emitted)

    def test_emit_start_game(self):
        self.current_event_emitted = False
        events.push_handlers(start_game=self.react_to_event)
        events.emit_start_game()
        self.assertTrue(self.current_event_emitted)
