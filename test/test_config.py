# -*- coding: utf-8 -*-
from model import Config
from unittest import TestCase


class TestConfig(TestCase):
    def test_change_time(self):
        c = Config()
        c.time_speed = 1
        c.change_time_speed(1)
        self.assertEquals(c.time_speed, 2)
        c.time_speed = 1
        c.change_time_speed(-1)
        self.assertEquals(c.time_speed, 0)

    def test_change_time_limit_break(self):
        c = Config()
        c.time_speed = 4
        c.change_time_speed(1)
        self.assertEquals(c.time_speed, 0)
        c.change_time_speed(-1)
        self.assertEquals(c.time_speed, 4)
