import pygame
import config
import json

class CraftingUI:
    def __init__(self) -> None:
        self.__box_width = config.UI_SCALE
        self.__page = 0

        with open("data/recipes.json", "r") as recipes:
            recipes = json.load(recipes)
            self.__recipe_book = self.__generate_recipe_book(recipes)


    def __generate_recipe_book(self, recipes: dict) -> dict:
        """Sorts recipes into groups."""

        recipe_book = {}

        for i in range(len(recipes) // (config.CRAFTING_COLUMNS * config.CRAFTING_ROWS) + 1):
            recipe_book[i] = {}

        for index, recipe in enumerate(recipes):
            recipe_book[index // (config.CRAFTING_COLUMNS * config.CRAFTING_ROWS)][recipe] = recipes[recipe]

        return recipe_book


    def __render_box(self, x: int, y: int, screen, item_texture, colour: tuple) -> None:

        background_box = pygame.Rect(x, y, self.__box_width, self.__box_width)
        pygame.draw.rect(screen, colour, background_box)

        item_x = x + self.__box_width // 2 - config.ITEM_SIZE // 2
        item_y = y + self.__box_width // 2 - config.ITEM_SIZE // 2
        
        image = pygame.image.load(item_texture)
        screen.blit(image, (item_x, item_y))


    def render_recipes(self, screen, inventory, inventory_ui) -> None:

        if not(inventory_ui.is_open()):
            return

        with open("data/items.json", "r") as item_data:
            item_data = json.load(item_data)

        x = config.HOTBAR_X
        y = config.CRAFTING_UI_Y

        for num, recipe in enumerate(self.__recipe_book[self.__page]):

            if inventory.has_ingredients(self.__recipe_book[self.__page][recipe]["ingredients"]):
                colour = (50, 50, 50)

            else: 
                colour = (203, 76, 78)

            texture = item_data[recipe]["texture"]
            self.__render_box(x, y, screen, texture, colour)

            x += self.__box_width

            if num == config.CRAFTING_COLUMNS * config.CRAFTING_ROWS - 1:
                y += config.UI_SCALE
                x = self.__box_width


    def get_slot_at_position(self, mouse_position: tuple, inventory_ui) -> int | None:

        if not inventory_ui.is_open():
            return None

        mouse_x, mouse_y = mouse_position

        for row in range(config.CRAFTING_ROWS):
            for column in range(config.CRAFTING_COLUMNS):
                slot = row * config.CRAFTING_ROWS + column
                x = config.HOTBAR_X + column * self.__box_width
                y = config.CRAFTING_UI_Y + row * self.__box_width
                slot_rect = pygame.Rect(x, y, self.__box_width, self.__box_width)

                if slot_rect.collidepoint(mouse_x, mouse_y):
                    return slot
            

            


