# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.scene import Scene
from cocos.sprite import Sprite
from controller import Core
from model import Config
from unittest import TestCase, skip
from unittest.mock import MagicMock, patch
from viewer import Gallery
from viewer.widgets import ButtonState, MultiStateButton

__author__ = 'Bárdos Dávid'


class TestMultiStateButton(TestCase):
    def setUp(self):
        Core()
        gallery = Gallery()
        self.config = Config()
        director.init(self.config.window_width, self.config.window_height)
        self.events = MagicMock()
        self.sprite_start = Sprite(gallery["button"]["start"])
        self.sprite_stop = Sprite(gallery["button"]["stop"])
        state_start = ButtonState(sprite=self.sprite_start,
                                  event=self.events.start)
        state_stop = ButtonState(sprite=self.sprite_stop,
                                 event=self.events.stop)
        self.switch = MultiStateButton(states=[state_start, state_stop],
                                       scale=0.66)

    def test__update_sprite(self):
        self.assertEqual(self.switch.children[1][1], self.sprite_start)
        self.assertEqual(self.switch.sprite.scale, self.switch.original_scale)
        self.switch.current_state +=1
        self.switch._update_sprite()
        self.assertEqual(self.switch.children[1][1], self.sprite_stop)
        self.assertEqual(self.switch.sprite.scale, self.switch.original_scale)

    def test__action_left_click(self):
        current_event = self.switch.event
        self.switch._action(1)
        self.assertEqual(1, self.switch.current_state)
        self.assertTrue(current_event.called)

    def test__action_right_click_while_diabled(self):
        current_event = self.switch.event
        self.switch._action(3)
        self.assertEqual(0, self.switch.current_state)
        self.assertFalse(current_event.called)

    def test__action_right_click_while_enabled(self):
        current_event = self.switch.event
        self.switch.backward_cycle_enabled = True
        self.switch._action(3)
        self.assertEqual(1, self.switch.current_state)
        self.assertTrue(current_event.called)

    @patch("viewer.widgets.MultiStateButton._update_sprite")
    def test__update_state_forward(self, mocked_function):
        self.switch._update_state(1)
        self.assertEqual(1, self.switch.current_state)
        self.assertTrue(mocked_function.called)

    @patch("viewer.widgets.MultiStateButton._update_sprite")
    def test__update_state_backward(self, mocked_function):
        self.switch._update_state(-1)
        self.assertEqual(1, self.switch.current_state)
        self.assertTrue(mocked_function.called)

    @skip("For manual use only.")
    def test_manually(self):
        director.run(scene=Scene(self.switch))
