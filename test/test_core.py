# -*- coding: utf-8 -*-
from controller import Core, events
from model import Game
from unittest import TestCase
from unittest.mock import patch


class TestCore(TestCase):
    def test_start_game(self):
        self.is_start_emitted = False
        c = Core()
        events.push_handlers(show_world_map=self.set_start_emitted)
        c.start_game()
        self.assertTrue(self.is_start_emitted)

    def set_start_emitted(self, *args):
        self.is_start_emitted = True

    def test_query_actor(self):
        with patch.object(Game, "query_train", return_value=None):
            c = Core()
            c.game = Game("")
            c.query_train("some string")
            self.assertTrue(c.game.query_train.called)



