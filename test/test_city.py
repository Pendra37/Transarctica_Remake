# -*- coding: utf-8 -*-
from unittest import TestCase
from model import City


class TestCity(TestCase):
    def test_calculate_tiles(self):
        c1 = City("London", x=5, y=1, x2=5, y2=1, city_type="normal")
        c2 = City("Berlin", 3, 9, 4, 10, "mammoth market")
        self.assertListEqual(c1.tiles, [(5, 1)])
        self.assertListEqual(c2.tiles, [(3, 9), (3, 10), (4, 9), (4, 10)])
