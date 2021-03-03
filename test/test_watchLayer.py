# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.scene import Scene
from controller import Core
from model import Config
from viewer.watchlayer import WatchLayer
from unittest import TestCase


class TestWatchLayer(TestCase):
    def test_init(self):
        self.watch_layer = WatchLayer()
        scene = Scene(self.watch_layer)
        # director.run(scene)

    def setUp(self):
        Core()
        self.config=Config()
        director.init(self.config.window_width, self.config.window_height)
