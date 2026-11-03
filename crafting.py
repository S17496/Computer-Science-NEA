import json
import items


class Crafting:
    def __init__(self) -> None:
        with open("data/recipes.json", "r") as file:
            self.__recipes = json.load(file)

        with open("data/items.json", "r") as file:
            self.__item_data = json.load(file)


    def craft(self, recipe_id: str, player) -> bool:

        inventory = player.get_inventory()

        recipe = self.__recipes[recipe_id]
        ingredients = recipe["ingredients"]
        result = recipe["result"]

        if inventory.has_ingredients(ingredients):

            item_data = self.__item_data[result["id"]]
            item_class = getattr(items, item_data["class"])
            crafted_item = item_class(result["id"], result["quantity"])

            if player.get_hand() is None:
                player.set_hand(crafted_item)

            else:
                if not(player.get_hand().add_one()):
                    return False

            for ingredient_id in ingredients:
                quantity_needed = ingredients[ingredient_id]
                inventory.remove_quantity(ingredient_id, quantity_needed)

            return True

        return False
