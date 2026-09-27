import json

import items_file as items


class Crafting:
    def __init__(self, recipes_path: str = "recipes.json") -> None:
        with open(recipes_path, "r") as file:
            self.__recipes = json.load(file)

        with open("item_data.json", "r") as file:
            self.__item_data = json.load(file)

    def craft(self, recipe_id: str, inventory) -> bool:
        pass
