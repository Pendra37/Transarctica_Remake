# -*- coding: utf-8 -*-


class RecWagon(object):
    """model of a wagon"""
    def __init__(self, wagon_name, screen_name, width, height, net_weight, capacity, storage, units, special, critical, rarity, avg_price, display_image, combat_image, desc, base_id, damage, M1, M2, M3):
        self.wagon_name = wagon_name
        self.screen_name = screen_name
        self.width = width
        self.height = height
        self.net_weight = net_weight
        self.capacity = capacity
        self.storage = storage
        self.units = units
        self.special = special
        self.critical = critical
        self.rarity = rarity
        self.avg_price = avg_price
        self.display_image = display_image
        self.combat_image = combat_image
        self.desc = desc
        self.base_id = base_id
        self.damage = damage
        self.M1 = M1
        self.M2 = M2
        self.M3 = M3
        #if city_type in self.valid_types:
        #    self.type = city_type
        #else:
        #    raise ValueError
