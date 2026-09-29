import json

import items_file as items


class Crafting:
    def __init__(self) -> None:
        with open("recipes.json", "r") as file:
            self.__recipes = json.load(file)

        with open("item_data.json", "r") as file:
            self.__item_data = json.load(file)

    def craft(self, recipe_id: str, inventory) -> None:
            
        recipe = self.__recipes[recipe_id]
        ingredients = recipe["ingredients"]

        if inventory.has_ingredients(ingredients):

            for ingredient_id in recipe["ingredients"]:
                # Removes ingredients from inventory
                quantity_needed = ingredients[ingredient_id]
                inventory.remove_quantity(ingredient_id, quantity_needed)

                # Adds item to inventory

