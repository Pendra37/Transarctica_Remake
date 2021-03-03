# -*- coding: utf-8 -*-


class RecItem(object):
    """model of an item"""
    def __init__(self, item_name, screen_name, net_weight, storage, special, CQCV, LRCV, HuntV, BuildV, display_image, desc, supply, market, avg_price):
        self.item_name = item_name
        self.screen_name = screen_name
        self.net_weight = net_weight
        self.storage = storage
        self.special = special
        self.CQCV = CQCV
        self.LRCV = LRCV
        self.HuntV = HuntV
        self.BuildV = BuildV
        self.display_image = display_image
        self.desc = desc
        self.supply = supply
        self.market = market 
        self.avg_price = avg_price

        #if city_type in self.valid_types:
        #    self.type = city_type
        #else:
        #    raise ValueError
