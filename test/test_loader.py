# -*- coding: utf-8 -*-
from controller import Loader
from unittest import TestCase


class TestLoader(TestCase):
    def test_load_cities(self):
        cities = Loader.load_cities("demo")
        self.assertListEqual(cities["by_name"]["London"].tiles, [(4, 4)])
        self.assertListEqual(cities["by_tile"][(4, 4)].tiles, [(4, 4)])
        self.assertListEqual(cities["by_name"]["Berlin"].tiles, [(0, 0), (0, 1), (0, 2)])
        self.assertListEqual(cities["by_tile"][(0, 1)].tiles, [(0, 0), (0, 1), (0, 2)])
