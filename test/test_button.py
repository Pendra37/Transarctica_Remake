# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.scene import Scene
from cocos.sprite import Sprite
from controller import Core
from unittest.mock import MagicMock
from model import Config
from unittest import TestCase, skip
from viewer import Gallery
from viewer.widgets import Button, ButtonState


class TestButton(TestCase):
    def emit_event(self):
        self.is_event_emitted = True

    def setUp(self):
        Core()
        g = Gallery()
        self.config = Config()
        director.init(self.config.window_width, self.config.window_height)
        state = ButtonState(sprite=Sprite(g.content["button"]["gear"]),
                            event=self.emit_event)
        self.button = Button(state=state, scale=0.75)
        self.button.position = 100, 100
        self.is_event_emitted = False

    def test_on_mouse_press(self):
        self.button.on_mouse_press(105, 105, 1, [])
        self.assertTrue(self.button.is_downscaled)

    def test_is_pressed(self):
        self.assertTrue(self.button._is_pressed((105, 105)))
        self.assertFalse(self.button._is_pressed((95, 105)))
        self.assertFalse(self.button._is_pressed((105, 95)))

    def test_on_mouse_release_over_button(self):
        self.button.is_downscaled = True
        self.button.on_mouse_release(105, 105, 1, [])
        self.assertFalse(self.button.is_downscaled)
        self.assertTrue(self.is_event_emitted)

    def test_on_mouse_release_not_over_button(self):
        self.button.is_downscaled = True
        self.button.on_mouse_release(95, 105, 1, [])
        self.assertFalse(self.button.is_downscaled)
        self.assertFalse(self.is_event_emitted)

    def test__action(self):
        self.button.states[0] = MagicMock()
        self.button._action(1)
        self.assertTrue(self.button.states[0].event.called)

    @skip("For manual use only.")
    def test_manually(self):
        director.run(scene=Scene(self.button))
