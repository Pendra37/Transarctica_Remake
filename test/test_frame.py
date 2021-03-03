# -*- coding: utf-8 -*-
from cocos.director import director
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.text import Label
from viewer.widgets import Frame
from unittest import skip, TestCase


class TestFrame(TestCase):
    @skip("Skipped as it is only for manual run.")
    def test_add(self):
        positions = {"left": (320, 249.0),
                     "right": (101, 249.0),
                     "top": (254.0, 204),
                     "bottom": (254.0, 240)}
        for side in positions:
            frame = Frame(background_color=(0, 0, 98, 255), side=side)
            frame.position = 320, 240
            layer = Layer()
            scene = Scene()
            layer.add(frame)
            scene.add(layer)
            label = Label("Hello World")
            label_new = Label("Hello World again")
            frame.add(label)
            frame.add(label_new)
            # self.assertTupleEqual(positions[side], (frame.x, frame.y))
            # director.run(scene)

    def test_padding(self):
        frame = Frame()
        frame.padding(top=9, bottom=-1, left=7)
        paddings = frame.padding()
        self.assertDictEqual(paddings, {"left": 7, "right": 0, "top": 9, "bottom": -1})

    def test_margins(self):
        frame = Frame()
        frame.margin(top=9, bottom=-1, left=7)
        margins = frame.margin()
        self.assertDictEqual(margins, {"left": 7, "right": 0, "top": 9, "bottom": -1})

    def test_borders(self):
        frame = Frame()
        frame.border(top=9, bottom=-1, left=7)
        borders = frame.border()
        self.assertDictEqual(borders, {"left": 7, "right": 0, "top": 9, "bottom": -1})

    def test_paddig_settings(self):
        frame_big = Frame(background_color=(0, 0, 98, 255))
        frame_big.side = "bottom"
        frame_big.padding(left=10, right=0, top=10, bottom=10)
        frame_small = Frame(background_color=(0, 0, 49, 255))
        label = Label("Hello World")
        label_new = Label("Hello World again")
        frame_small.add(label)
        frame_small_new = Frame(background_color=(0, 49, 0, 255))
        frame_small_new.add(label_new)
        frame_big.add(frame_small)
        frame_big.add(frame_small_new)
        frame_big.position = 320, 240
        # it was used for manual assertion
        # director.run(Scene(frame_big))

    def setUp(self):
        director.init()
