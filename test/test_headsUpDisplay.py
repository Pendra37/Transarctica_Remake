# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.scene import Scene
from model import Config
from viewer.hud import HeadsUpDisplay
from unittest import TestCase, skip


class TestHeadsUpDisplay(TestCase):
    def setUp(self):
        self.config = Config()
        self.config.window_width = 1024
        resolution = (self.config.window_width, self.config.window_height)
        director.init(*resolution)
        self.hud = HeadsUpDisplay()
        self.scene = Scene()
        self.scene.add(self.hud)

    @skip("For manual use only.")
    def test_load_old_dashboard(self):
        director.run(self.scene)
