# -*- coding: utf-8 -*-
from model import Config
from os import listdir
from pyglet.image import load
from pyglet.image import load_animation
from re import match

class Gallery(object):
    """
    Loads graphical resources on first use.
    Serves all of them later.
    """
    content = {}
    resources = {}

    def __init__(self):
        """initializer"""
        if not self.resources:
            self._load_resources()
        if self.resources and not self.content:
            self._load_content()

    def __getitem__(self, item):
        return self.content[item]

    def _load_content(self):
        """generates content from resources"""
        for extension in Config.graphics_format:
            if extension in self.resources:
                for resource in self.resources[extension]:
                    pattern = r"(?P<type>[A-Za-z]+)_(?P<name>[\w_\.]+)\.(?P<extension>\w+)"
                    matched_file_name = match(pattern, resource)
                    content_group = matched_file_name.group("type")
                    if content_group not in self.content:
                        self.content[content_group] = {}
                    if extension == "gif":
                        self.content[content_group][matched_file_name.group("name")] = load_animation("{}/{}".format(Config.resources, resource))
                    else:
                        self.content[content_group][matched_file_name.group("name")] = load("{}/{}".format(Config.resources, resource))

    def _load_resources(self):
        """generates resources dictionary"""
        file_list = listdir(Config.resources)
        for file_item in file_list:
            extension = file_item.split(".")[-1].lower()
            if extension in self.resources:
                self.resources[extension].append(file_item)
            else:
                self.resources[extension] = [file_item]
