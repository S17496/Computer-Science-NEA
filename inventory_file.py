import config_file as conf
import tile_file as t
import json

class Item:
    def __init__(self, id: str, quantity: int) -> None:
        with open("item_data.json", "r") as file:
            item_data = json.load(file)[id]
        self._name = item_data["name"]
        self._quantity = quantity 
        self._max_stack = item_data["max_stack"]

    # Getters and setters
    def get_name(self) -> str:
        return self._name

    def get_quantity(self) -> int:
        return self._quantity

    def get_max_stack(self) -> int:
        return self._max_stack

    def set_quantity(self, quantity: str) -> None:
        self._quantity = quantity

class Pickaxe(Item):
    def __init__(self, id: str, quantity: int) -> None:
        super().__init__(id, quantity)
        with open("item_data.json", "r") as file:
                    item_data = json.load(file)[id]
        self.__pickaxe_power = item_data["pickaxe_power"]
        self.__pickaxe_speed = item_data["pickaxe_speed"]

    def break_tile(self, tile: t.Tile) -> None:
        if self.__pickaxe_power > tile.get_hardness():
            pass 
            # UNFINISHED

    def get_pickaxe_speed(self) -> int:
        return self.__pickaxe_speed

class TileItem(Item):
    def __init__(self, id: str, quantity: str) -> None:
        super().__init__(id, quantity)
        with open("item_data.json", "r") as file:
            item_data = json.load(file)[id]
        self.__tile_id = item_data["tile_id"]

    def get_tile(self) -> t.Tile:
        return self.__tile

class Inventory:
    def __init__(self) -> None:
        self.__selected_slot = 0
        
        # Fills in all inventory slots with placeholder None
        self.__items = []
        for _ in range(conf.INVENTORY_SIZE):
            self.__items.append(None)


    # Getters and setters
    def get_items(self) -> list:
        return self.__items

    def add_item(self, item: Item) -> None:
        for i in range(conf.INVENTORY_SIZE):
            if self.__items[i] != None:
                if item.get_name() == self.__items[i].get_name() and self.__items[i].get_quantity() < self.__items[i].get_max_stack():
                    self.__items[i].set_quantity(self.__items[i].get_quantity() + 1)
                    break
        else:
            for i in range(conf.INVENTORY_SIZE):
                if self.__items[i] == None:
                    self.__items[i] = item
                    break

    def get_selected_slot(self) -> int:
        return self.__selected_slot

    def set_selected_slot(self, slot: int) -> None:
        self.__selected_slot = slot

    def get_selected_item(self) -> Item:
        return self.__items[self.__selected_slot]

