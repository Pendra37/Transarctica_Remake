# -*- coding: utf-8 -*-
from model import RecCity, RecWagon, RecItem, Config
from xml.etree.ElementTree import ElementTree, Element
import ast
from cocos.director import director

class XMLParser(object):
    """collection of statick methods to load different resources"""
    @staticmethod
    def load_cities(game_name):
        """load cities from the XML file set in settings"""
        cities = {"by_name": {}, "by_tile": {}}
        xml_path = "{}/{}{}".format(Config.resources, game_name, Config.cities)
        xml_root = ElementTree().parse(xml_path)
        for city in list(xml_root):  # iterating through cities
            city_name = city.get("name")
            city_tile_x=city.find("tile_x")
            city_tile_y=city.find("tile_y") 
            city_width=city.find("width") 
            city_height=city.find("height")
            city_event_x=city.find("event_x") 
            city_event_y=city.find("event_y")
            city_type=city.find("type")
            city_supply=city.find("supply")
            # creating City object
            Config.conf_cities_by_tile[city_tile_x.text+","+city_tile_y.text] = RecCity(city_name, city_tile_x.text, city_tile_y.text, city_width.text, city_height.text, city_event_x.text, city_event_y.text, city_type.text, city_supply.text)
            Config.conf_cities_by_name[city_name] = Config.conf_cities_by_tile[city_tile_x.text+","+city_tile_y.text]

    def load_wagons(game_name):
        """load wagons from the XML file set in settings"""
        wagons = {}
        xml_path = "{}/{}{}".format(Config.resources, game_name, Config.wagons)
        xml_root = ElementTree().parse(xml_path)
        for wagon in list(xml_root):  # iterating through wagons
            wagon_name = wagon.get("name")
            screen_name=wagon.find("screen_name")
            width=wagon.find("width") 
            height=wagon.find("height") 
            net_weight=wagon.find("net_weight")
            capacity=wagon.find("capacity") 
            storage=wagon.find("storage")
            units=wagon.find("units")
            special=wagon.find("special")
            critical=wagon.find("critical")
            rarity=wagon.find("rarity")
            avg_price=wagon.find("avg_price")
            display_image=wagon.find("display_image") 
            combat_image=wagon.find("combat_image")
            desc=wagon.find("desc")
            # creating wagon object
            Config.conf_wagons[len(Config.conf_wagons)] = RecWagon(wagon_name, screen_name.text, width.text, height.text, net_weight.text, capacity.text, storage.text, units.text, special.text, critical.text, rarity.text, avg_price.text, display_image.text, combat_image.text, desc.text, len(Config.conf_wagons), 0, "", "", "")
            if storage.text not in Config.conf_storage_type:
                Config.conf_storage_type[storage.text]=storage.text
        cnt=len(Config.conf_wagons)
        Config.base_wagon_range=cnt
        for wagon in range(cnt): 
            for damage in range(1,4): 
                Config.conf_wagons[len(Config.conf_wagons)] = RecWagon(Config.conf_wagons[wagon].wagon_name+"_D"+str(damage), Config.conf_wagons[wagon].screen_name, Config.conf_wagons[wagon].width, Config.conf_wagons[wagon].height, Config.conf_wagons[wagon].net_weight, Config.conf_wagons[wagon].capacity, Config.conf_wagons[wagon].storage, Config.conf_wagons[wagon].units, Config.conf_wagons[wagon].special, Config.conf_wagons[wagon].critical, Config.conf_wagons[wagon].rarity, Config.conf_wagons[wagon].avg_price, Config.conf_wagons[wagon].display_image, Config.conf_wagons[wagon].combat_image, Config.conf_wagons[wagon].desc, Config.conf_wagons[wagon].base_id, damage, "", "", "")

    def load_items(game_name):
        """load items from the XML file set in settings"""
        item = {}
        xml_path = "{}/{}{}".format(Config.resources, game_name, Config.items)
        xml_root = ElementTree().parse(xml_path)
        for item in list(xml_root):  # iterating through items
            item_name = item.get("name")
            screen_name=item.find("screen_name")
            net_weight=item.find("net_weight")
            storage=item.find("storage")
            special=item.find("special")
            CQCV=item.find("CQCV")
            LRCV=item.find("LRCV")
            HuntV=item.find("HuntV")
            BuildV=item.find("BuildV")
            display_image=item.find("display_image") 
            desc=item.find("desc")
            supply=item.find("supply")
            market=item.find("market")
            avg_price=item.find("avg_price")
            # creating item object
            Config.conf_items[len(Config.conf_items)] = RecItem(item_name, screen_name.text, net_weight.text, storage.text, special.text, CQCV.text, LRCV.text, HuntV.text, BuildV.text, display_image.text, desc.text, supply.text, market.text, avg_price.text)
        #for i in Config.conf_wagons:
        #    Config.conf_items[len(Config.conf_items)] = RecItem(Config.conf_wagons[i].wagon_name, Config.conf_wagons[i].screen_name, "0", "wagon", "wagon", Config.conf_wagons[i].display_image, Config.conf_wagons[i].desc, "wagon", "wagon", Config.conf_wagons[i].avg_price)

    def indent(elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
          if not elem.text or not elem.text.strip():
            elem.text = i + "  "
          if not elem.tail or not elem.tail.strip():
            elem.tail = i
          for elem in elem:
            indent(elem, level+1)
          if not elem.tail or not elem.tail.strip():
            elem.tail = i
        else:
          if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

    def save_game(game_name, object_name, object):
        xml_path = "{}/{}{}".format(Config.resources, game_name, "_qso.xml")
        tree = ElementTree()
        xml_root=tree.parse(xml_path)
        for game_object in list(xml_root): 
            if game_object.get("name")=="Common":
                mover = director.core.query_mover("Transarctica")
                game_object.find("timestamp").text=str(mover.current_timestamp())
                for item in Config.coal_mine:
                    game_object.find("CMP"+str(item)).text=str(Config.coal_mine[item])
                game_object.find("tunnel_block_chance").text=str(Config.tunnel_block_chance)
                game_object.find("nr_of_POI").text=str(len(mover.map.POI))
                for id in mover.map.POI:
                    game_object.find("POI"+str(id)).text=str(mover.map.POI[id])
            elif game_object.get("name")=="Transarctica":
                mover = director.core.query_mover("Transarctica")
                game_object.find("direction").text=mover.direction
                game_object.find("hpz").text=str(mover.hpz)
                game_object.find("engine_temp").text=str(mover.engine_temp)
                game_object.find("boiler_pressure").text=str(mover.boiler_pressure)
                game_object.find("is_in_reverse").text=str(mover.is_in_reverse)
                game_object.find("is_break_released").text=str(mover.is_break_released)
                game_object.find("speed").text=str(mover.speed)
                game_object.find("Speed_Regulator").text=str(mover.Speed_Regulator)
                game_object.find("target_speed").text=str(mover.target_speed)
                game_object.find("current_position").text=str(mover.current_position)
                game_object.find("nr_of_wagons").text=str(len(mover.train_layout))
                for wg in mover.train_layout:
                    game_object.find("wagon_"+str(wg)).text=str(mover.train_layout[wg])
                for item in mover.cargo_manifest:
                    game_object.find("stock_item_"+str(item)).text=str(mover.cargo_manifest[item])
                #    new=Element('stock_item_'+str(item))
                #    new.text=str(mover.cargo_manifest[item])
                #    game_object.append(new)
                #for item in range(len(Config.coal_mine)-1):
                #    game_object.find("stock_item_"+str(item)).text=str(mover.known_coal_mine[item])
                ##   new=Element('CMP'+str(item))
                #    new.text=str(Config.coal_mine[item])
                #   game_object.append(new)
            elif game_object.get("name")[:7]=="VUTrain":
                mover = director.core.query_mover(game_object.get("name"))
                game_object.find("direction").text=mover.direction
                game_object.find("hpz").text=str(mover.hpz)
                game_object.find("is_in_reverse").text=str(mover.is_in_reverse)
                game_object.find("is_break_released").text=str(mover.is_break_released)
                game_object.find("speed").text=str(mover.speed)
                game_object.find("Speed_Regulator").text=str(mover.Speed_Regulator)
                game_object.find("target_speed").text=str(mover.target_speed)
                game_object.find("current_position").text=str(mover.current_position)
                game_object.find("is_intact").text=str(mover.is_intact)
                game_object.find("respawn_timestamp").text=str(mover.respawn_timestamp)
                game_object.find("force_rating").text=str(mover.force_rating)

            elif game_object.get("name")[:6]=="Roamer":
                mover = director.core.query_mover(game_object.get("name"))
                game_object.find("direction").text=mover.direction
                game_object.find("is_break_released").text=str(mover.is_break_released)
                game_object.find("speed").text=str(mover.speed)
                game_object.find("current_position").text=str(mover.current_position)
                game_object.find("force_rating").text=str(mover.force_rating)
                game_object.find("roamer_type").text=str(mover.roamer_type)

        tree.write(xml_path)


    def load_game(game_name, object_name, object):
        xml_path = "{}/{}{}".format(Config.resources, game_name, "_qso.xml")
        tree = ElementTree()
        xml_root=tree.parse(xml_path)
        for game_object in list(xml_root):  
            if game_object.get("name")=="Common":
                Config.start_timestamp=float(game_object.find("timestamp").text)
                for item in range(Config.coal_mine_count*2):
                    Config.coal_mine[str(item)]=ast.literal_eval(game_object.find('CMP'+str(item)).text)
                Config.tunnel_block_chance=float(game_object.find("tunnel_block_chance").text)
                Config.loaded_objects["POI"]= {}
                for id in range(int(game_object.find("nr_of_POI").text)):
                    Config.loaded_objects["POI"][str(id)]=ast.literal_eval(game_object.find('POI'+str(id)).text)
            elif game_object.get("name")=="Transarctica":
                Config.loaded_objects["Transarctica"] = {} 
                Config.loaded_objects["Transarctica"]["direction"]=str(game_object.find("direction").text)
                Config.loaded_objects["Transarctica"]["is_in_reverse"]=bool((game_object.find("is_in_reverse").text).replace("False", "")) 
                Config.loaded_objects["Transarctica"]["is_break_released"]=bool((game_object.find("is_break_released").text).replace("False", "")) 
                Config.loaded_objects["Transarctica"]["speed"]=float(game_object.find("speed").text)
                Config.loaded_objects["Transarctica"]["Speed_Regulator"]=float(game_object.find("Speed_Regulator").text)
                Config.loaded_objects["Transarctica"]["target_speed"]=float(game_object.find("target_speed").text)
                Config.loaded_objects["Transarctica"]["hpz"]=float(game_object.find("hpz").text)
                Config.loaded_objects["Transarctica"]["engine_temp"]=float(game_object.find("engine_temp").text)
                Config.loaded_objects["Transarctica"]["boiler_pressure"]=float(game_object.find("boiler_pressure").text)
                Config.loaded_objects["Transarctica"]["current_position"]=ast.literal_eval(game_object.find('current_position').text)
                Config.loaded_objects["Transarctica"]["start_train"]=[]
                for wg in range(int(game_object.find("nr_of_wagons").text)):
                    Config.loaded_objects["Transarctica"]["start_train"].append(Config.conf_wagons[int(game_object.find('wagon_'+str(wg)).text)].wagon_name)

                Config.start_items.clear()
                Config.start_items_values.clear()
                for item in Config.conf_items: 
                    tempd=ast.literal_eval(game_object.find('stock_item_'+str(item)).text)
                    if tempd["hold"]>0:
                        Config.start_items[Config.conf_items[item].item_name]=int(tempd["hold"])
                        Config.start_items_values[Config.conf_items[item].item_name]=int(tempd["value"])

            elif game_object.get("name")[:7]=="VUTrain":
                Config.loaded_objects[game_object.get("name")] = {} 
                Config.loaded_objects[game_object.get("name")]["direction"]=str(game_object.find("direction").text)
                Config.loaded_objects[game_object.get("name")]["is_in_reverse"]=bool((game_object.find("is_in_reverse").text).replace("False", "")) 
                Config.loaded_objects[game_object.get("name")]["is_break_released"]=bool((game_object.find("is_break_released").text).replace("False", "")) 
                Config.loaded_objects[game_object.get("name")]["speed"]=float(game_object.find("speed").text)
                Config.loaded_objects[game_object.get("name")]["Speed_Regulator"]=float(game_object.find("Speed_Regulator").text)
                Config.loaded_objects[game_object.get("name")]["target_speed"]=float(game_object.find("target_speed").text)
                Config.loaded_objects[game_object.get("name")]["hpz"]=float(game_object.find("hpz").text)
                Config.loaded_objects[game_object.get("name")]["respawn_timestamp"]=float(game_object.find("respawn_timestamp").text)
                Config.loaded_objects[game_object.get("name")]["is_intact"]=bool((game_object.find("is_intact").text).replace("False", "")) 
                Config.loaded_objects[game_object.get("name")]["current_position"]=ast.literal_eval(game_object.find('current_position').text)
                Config.loaded_objects[game_object.get("name")]["force_rating"]=float(game_object.find("force_rating").text)

            elif game_object.get("name")[:6]=="Roamer":
                Config.loaded_objects[game_object.get("name")] = {} 
                Config.loaded_objects[game_object.get("name")]["direction"]=str(game_object.find("direction").text)
                Config.loaded_objects[game_object.get("name")]["is_break_released"]=bool((game_object.find("is_break_released").text).replace("False", "")) 
                Config.loaded_objects[game_object.get("name")]["speed"]=float(game_object.find("speed").text)
                Config.loaded_objects[game_object.get("name")]["roamer_type"]=str(game_object.find("roamer_type").text)
                Config.loaded_objects[game_object.get("name")]["current_position"]=ast.literal_eval(game_object.find('current_position').text)
                Config.loaded_objects[game_object.get("name")]["force_rating"]=float(game_object.find("force_rating").text)


    def stuff(game_name, object_name, object):
        if object_name == game_object.get("name"):
            Config.start_position["X"]=int(game_object.find("current_position_X").text)
            Config.start_position["Y"]=int(game_object.find("current_position_Y").text)
            Config.start_timestamp=float(game_object.find("timestamp").text)
            Config.start_train.clear()
            for wg in range(int(game_object.find("nr_of_wagons").text)):
                Config.start_train.append(Config.conf_wagons[int(game_object.find('wagon_'+str(wg)).text)].wagon_name)
            Config.start_items.clear()
            Config.start_items_values.clear()
            for item in Config.conf_items: 
                tempd=ast.literal_eval(game_object.find('stock_item_'+str(item)).text)
                if tempd["hold"]>0:
                    Config.start_items[Config.conf_items[item].item_name]=int(tempd["hold"])
                    Config.start_items_values[Config.conf_items[item].item_name]=int(tempd["value"])
            for item in range(Config.coal_mine_count*2):
                Config.coal_mine[str(item)]=ast.literal_eval(game_object.find('CMP'+str(item)).text)



    def load_lang_file(game_name, lang):
        xml_path = "{}/{}{}".format(Config.resources, game_name,"_lang_file.xml")
        tree = ElementTree()
        xml_root=tree.parse(xml_path)
        for language in list(xml_root):  
            if lang == language.get("lang"):
                for lang_object in list(language):  
                    id = lang_object.get("id")
                    content = lang_object.text
                    Config.lang_file[id] = content                
