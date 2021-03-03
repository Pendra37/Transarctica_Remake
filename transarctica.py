# -*- coding: utf-8 -*-
from controller import Core
from viewer import UserInterface


class Application(object):
    """represents application"""
    def __init__(self):
        """initializer"""
        core = Core()
        user_interface = UserInterface(core)
        user_interface.show_title_screen()

a = Application()
