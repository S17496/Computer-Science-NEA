import config_file as conf
import items_file as items


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

    def add_item(self, item: items.Item) -> None:
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

    def get_selected_item(self) -> items.Item:
        return self.__items[self.__selected_slot]

