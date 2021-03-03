# -*- coding: utf-8 -*-
from model import Transarctica
from math import ceil
from unittest import TestCase


class TestTransarctica(TestCase):
    """test class of the player avatar"""
    train = Transarctica()

    def test_set_direction(self):
        with self.assertRaises(ValueError):
            self.train.set_direction("")
        self.train.set_direction("N")
        self.assertEqual(self.train.direction, "N")

    def test_set_target_speed(self):
        with self.assertRaises(ValueError):
            self.train.set_target_speed(-1)
        with self.assertRaises(ValueError):
            self.train.set_target_speed(301)
        self.train.set_target_speed(0)
        self.train.set_target_speed(300)

    def test_align_speed(self):
        test_normal_speed = 88
        test_speed_align_to_maximum = 294
        test_speed_align_to_minimum = 7
        # speeding to the max
        self.train.speed = test_speed_align_to_maximum
        self.train.set_target_speed(300)
        for i in range(ceil((self.train.maximum_speed - self.train.speed) / self.train.speeding_rate)):
            self.assertEqual(self.train.speed, test_speed_align_to_maximum + (i * self.train.speeding_rate))
            self.train.align_speed()
        self.assertEqual(self.train.speed, self.train.maximum_speed)
        # breaking to normal speed
        initial_speed = 100
        self.train.speed = initial_speed
        self.train.set_target_speed(test_normal_speed)
        for i in range(ceil((self.train.speed - test_normal_speed) / self.train.speeding_rate)):
            self.train.align_speed()
        self.assertEqual(self.train.speed, test_normal_speed)
        # breaking to the min
        self.train.speed = test_speed_align_to_minimum
        self.train.set_target_speed(0)
        for i in range(ceil((self.train.speed - self.train.minimum_speed) / self.train.speeding_rate)):
            self.assertEqual(self.train.speed, test_speed_align_to_minimum - (i * self.train.speeding_rate))
            self.train.align_speed()
        self.assertEqual(self.train.speed, self.train.minimum_speed)
        # speeding to normal speed
        initial_speed = 80
        self.train.speed = initial_speed
        self.train.set_target_speed(test_normal_speed)
        for i in range(ceil((test_normal_speed - initial_speed) / self.train.speeding_rate)):
            self.train.align_speed()
        self.assertEqual(self.train.speed, test_normal_speed)

