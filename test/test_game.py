# -*- coding: utf-8 -*-
from model import Game
from os.path import dirname
from unittest import TestCase


class TestGame(TestCase):
    def test_get_map_file_name(self):
        game = Game("test")
        path = dirname(dirname(__file__)).replace("\\", "/")
        expected = "{}/resources/test.tmx".format(path)
        self.assertEqual(expected, game.get_map_file_name())

    def test_query_train(self):
        game = Game("test")
        game.world_objects["trains"]["dummy"] = "dummy string"
        self.assertEqual("dummy string", game.query_train("dummy"))
