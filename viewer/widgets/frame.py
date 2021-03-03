# -*- coding: utf-8 -*-
from cocos.layer import Layer
from cocos.layer import ColorLayer


class Frame(Layer):
    """
    Used for grouping UI elements. Frame children are automatically shown.
    :param side: defines the first element position according to the next element
    :param background_color: tuple of (R, G, B, opacity)
    """
    _box_settings = ["margins", "borders", "padding"]
    _valid_expand_values = ["fit", "fill"]
    _valid_sides = ["left", "right", "top", "bottom", "manual"]

    def __init__(self, side="left", background_color=(0, 0, 0, 0), expand="fit"):
        """initializer"""
        Layer.__init__(self)
        self._borders = {"left": 0, "right": 0, "top": 0, "bottom": 0}
        self._margins = {"left": 0, "right": 0, "top": 0, "bottom": 0}
        self._padding = {"left": 0, "right": 0, "top": 0, "bottom": 0}
        self._check_arguments(expand, side)
        self.side = side
        self.expand = expand
        self.background_color = background_color
        self.width = 0
        self.height = 0
        self.add(ColorLayer(*background_color, width=0, height=0), name="background")

    def add(self, child, z=0, name=None):
        """own add function, so background color and ordering is covered"""
        Layer.add(self, child, z, name)
        if name != "background":
            self._update_dimensions()
            self._update_background_size()
            if self.side != "manual":
                self._update_children_position()
    
    def border(self, top=None, right=None, bottom=None, left=None):
        """
        Use this to manipulate borders or get the settings. Wrapper for the
            ugly _set_boxing method.
        :param top: changes top border
        :param right: changes right border
        :param bottom: changes bottom border
        :param left: changes left border 
        """
        return self._set_boxing("borders", bottom, left, right, top)

    def _check_arguments(self, expand, side):
        """checks special arguments and raises KeyErrors if something is wrong"""
        if side not in self._valid_sides:
            raise KeyError('Side argument value "{}" is invalid. It must be one of the following: {}'.format(side, self._valid_sides))
        if expand not in self._valid_expand_values:
            raise KeyError('Expand argument value "{}" is invalid. It must be one of the following: {}'.format(expand, self._valid_sides))

    def margin(self, top=None, right=None, bottom=None, left=None):
        """
        Use this to manipulate margins or get the settings. Wrapper for the
            ugly _set_boxing method.
        :param top: changes top margin
        :param right: changes right margin
        :param bottom: changes bottom margin
        :param left: changes left margin 
        """
        return self._set_boxing("margins", bottom, left, right, top)

    def _get_child_dimensions(self, child):
        """
        :param child: child of the frame
        :returns: (child width, child height)
        """
        try:
            width_origin = child.element.content_width
            height_origin = child.element.content_height
        except AttributeError:
            width_origin = child.width
            height_origin = child.height
        return width_origin, height_origin

    def padding(self, top=None, right=None, bottom=None, left=None):
        """
        Use this to manipulate padding or get the settings. Wrapper for the
            ugly _set_boxing method.
        :param top: changes top padding
        :param right: changes right padding
        :param bottom: changes bottom padding
        :param left: changes left padding
        """
        return self._set_boxing("padding", bottom, left, right, top)

    def _set_boxing(self, box_setting, bottom, left, right, top):
        """sets borders, padding or margins or simply return their values"""
        if box_setting not in self._box_settings:
            raise KeyError("Invalid box setting: {}. It must be one of the following: {}".format(box_setting, self._box_settings))
        if box_setting == "borders":
            attribute_to_change = self._borders
        elif box_setting == "margins":
            attribute_to_change = self._margins
        else:
            attribute_to_change = self._padding
        if top:
            attribute_to_change["top"] = top
        if right:
            attribute_to_change["right"] = right
        if bottom:
            attribute_to_change["bottom"] = bottom
        if left:
            attribute_to_change["left"] = left
        if not all([top, left, right, bottom]):
            return attribute_to_change

    def _update_background_size(self):
        """call it only form self.add"""
        self.get("background").width = self.width
        self.get("background").height = self.height

    def _update_children_position(self):
        """call it only from self.add"""
        current_postion = self._padding[self.side]
        for child in self.children[1:]:
            child_width, child_height = self._get_child_dimensions(child[1])
            positioning = {"left": (current_postion,
                                    (self.height-self._padding["top"]-self._padding["bottom"]-child_height)/2 + self._padding["bottom"]),
                           "right": (current_postion - child_width,
                                     (self.height-self._padding["top"]-self._padding["bottom"]-child_height)/2 + self._padding["bottom"]),
                           "top": ((self.width-self._padding["left"]-self._padding["right"]-child_width)/2 + self._padding["left"],
                                   (current_postion - child_height)),
                           "bottom": ((self.width-self._padding["left"]-self._padding["right"]-child_width)/2 + self._padding["left"], current_postion)}
            child[1].position = positioning[self.side]
            new_current_position = {"left": child_width,
                                    "right": -child_width,
                                    "top": -child_height,
                                    "bottom": child_height}
            current_postion += new_current_position[self.side]

    def _update_dimensions(self):
        """recalculates own size"""
        new_width, new_height = 0, 0
        for child in self.children[1:]:
            child_width, child_height = self._get_child_dimensions(child[1])
            formula = {"left": (new_width + child_width, max(new_height, child_height)),
                       "right": (new_width + child_width, max(new_height, child_height)),
                       "top": (max(new_width, child_width), new_height + child_height),
                       "bottom": (max(new_width, child_width), new_height + child_height),
                       "manual": (max(new_width, child_width), max(new_height, child_height))}
            new_width = formula[self.side][0]
            new_height = formula[self.side][1]
        new_width += self._padding["left"] + self._padding["right"]
        new_height += self._padding["top"] + self._padding["bottom"]
        self.width, self.height = new_width, new_height
