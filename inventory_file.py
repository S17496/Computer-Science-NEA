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

        for slot_item in self.__items:
            if slot_item is not None and slot_item.get_id() == item.get_id():

                free_space = slot_item.get_max_stack() - slot_item.get_quantity()
                transfer = min(free_space, item.get_quantity())

                slot_item.set_quantity(slot_item.get_quantity() + transfer)
                item.set_quantity(item.get_quantity() - transfer)

                if item.get_quantity() == 0:
                    return

        for i in range(len(self.__items)):
            if self.__items[i] is None:

                self.__items[i] = item.copy()
                item.set_quantity(0)
                return

    def remove_item(self, index: int) -> None:
        self.__items[index] = None

    def get_selected_slot(self) -> int:
        return self.__selected_slot

    def set_selected_slot(self, slot: int) -> None:
        if slot >= conf.HOTBAR_SIZE or slot < 0:
            return
        self.__selected_slot = slot

    def get_selected_item(self) -> items.Item:
        return self.__items[self.__selected_slot]

