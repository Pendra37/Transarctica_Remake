# -*- coding: utf-8 -*-


class ResolutionScaler(object):
    upscale = 8
    common_resolutions = [(320, 200),  # original
                          (320, 240),
                          (480, 272),
                          (640, 400),
                          (640, 480),
                          (800, 600),
                          (1024, 768),
                          (1280, 800),
                          (1280, 1024),
                          (1360, 768),
                          (1400, 1050),
                          (1440, 900),
                          (1440, 1080),  # 4:3 on 1080p
                          (1600, 900),
                          (1680, 1050),
                          (1600, 1200),
                          (1920, 1080),
                          (1920, 1200),
                          (2650, 1440),  # highest 16:9
                          (2560, 1600),  # highest 16:10
                          ]

    def __init__(self, width_height):
        """
        :param width_height: tuple of width_height
        initializer
        """
        self.width, self.height = width_height
        self.optimal_width = 320. * self.upscale
        self.optimal_height = 200. * self.upscale

    def get_ratio(self):
        """:returns: the optimal scaling ratio"""
        r = min(self.width/self.optimal_width, self.height/self.optimal_height)
        return r

    def get_dashboard_size(self):
        """:returns: current dashboard size"""
        ratio = self.get_ratio()
        dashboard_width = 320. * self.upscale * ratio
        dashboard_height = 40. * self.upscale * ratio
        return dashboard_width, dashboard_height

    def get_mainmenu_size(self):
        ratio = self.get_ratio()
        dashboard_width = 320. * self.upscale * ratio
        dashboard_height = 200. * self.upscale * ratio
        return dashboard_width, dashboard_height

    def get_POIdisplay_size(self):
        ratio = self.get_ratio()
        dashboard_width = 320. * self.upscale * ratio
        dashboard_height = 160. * self.upscale * ratio
        return dashboard_width, dashboard_height
