import pygame
import config
import json


class InventoryUI:
    def __init__(self) -> None:
        self.__box_width = config.UI_SCALE
        self.__open = False

    def render_hotbar(self, screen, hotbar_items: list, selected_slot: int) -> None:

        # Draw items and boxes
        x = config.HOTBAR_X
        y = config.HOTBAR_Y

        for i in range(len(hotbar_items)):

            colour = (50, 50, 50)
            if i == selected_slot:
                colour = (150, 150, 150)

            self.render_box(x, y, screen, hotbar_items[i], colour)
            x += self.__box_width


    def render_box(self, x: int, y: int, screen, item, colour: tuple) -> None:

        background_box = pygame.Rect(x, y, self.__box_width, self.__box_width)
        pygame.draw.rect(screen, colour, background_box)

        item_x = x + self.__box_width // 2 - config.ITEM_SIZE // 2
        item_y = y + self.__box_width // 2 - config.ITEM_SIZE // 2

        if item is None:
            return 
        
        image = pygame.image.load(item.get_texture())
        screen.blit(image, (item_x, item_y))



    def render_inventory(self, screen, inventory_items: list, selected_slot: int) -> None:

        if not(self.__open):
            # For rendering ONLY hotbar
            hotbar_items = []
            for i in range(config.HOTBAR_SIZE):
                hotbar_items.append(inventory_items[i])

            self.render_hotbar(screen, hotbar_items, selected_slot)
            return

        # Draw items and boxes
        x = config.HOTBAR_X
        y = config.HOTBAR_Y

        for i in range(config.INVENTORY_SIZE // config.HOTBAR_SIZE):
            for j in range(config.HOTBAR_SIZE):

                item_number = i * config.HOTBAR_SIZE + j

                colour = (50, 50, 50)
                if item_number == selected_slot:
                    colour = (150, 150, 150)

                self.render_box(x, y, screen, inventory_items[item_number], colour)

                x += self.__box_width
            y += self.__box_width
            x = config.HOTBAR_X

    def get_slot_at_position(self, mouse_position: tuple) -> int | None:
        if not self.__open:
            return None

        mouse_x, mouse_y = mouse_position

        for row in range(config.INVENTORY_SIZE // config.HOTBAR_SIZE):
            for column in range(config.HOTBAR_SIZE):
                slot = row * config.HOTBAR_SIZE + column
                x = config.HOTBAR_X + column * self.__box_width
                y = config.HOTBAR_Y + row * self.__box_width
                slot_rect = pygame.Rect(x, y, self.__box_width, self.__box_width)

                if slot_rect.collidepoint(mouse_x, mouse_y):
                    return slot

        return None

    def render_hand_item(self, screen, item) -> None:
        if not self.__open or item is None:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        image = pygame.image.load(item.get_texture())
        screen.blit(image, (mouse_x, mouse_y))

    def is_open(self) -> bool:
        return self.__open

    def change_state(self) -> None:
        self.__open = not(self.__open)


class CraftingUI:
    def __init__(self) -> None:
        self.__box_width = config.UI_SCALE
        self.__page = 0

        with open("data/recipes.json", "r") as recipes:
            recipes = json.load(recipes)
            self.__recipe_book = self.__generate_recipe_book(recipes)


    def __generate_recipe_book(self, recipes: dict) -> dict:
        """Sorts recipes into groups."""

        recipe_book = []

        for _ in range(len(recipes) // (config.CRAFTING_COLUMNS * config.CRAFTING_ROWS) + 1):
            recipe_book.append({})

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

        
    def get_page(self) -> int:
        return self.__page
            

    def get_item_id(self, slot_num: int) -> str:

        for num, id in enumerate(self.__recipe_book[self.__page]):

            if num == slot_num:
                return id


class HealthBar:

    def __init__(self) -> None:
        return

    def render_health_bar(self, screen, health: int, max_health: int) -> None:
        """Draws player's health bar on screen."""
        width = 200
        height = 20
        x = 1000
        y = 100

        pygame.draw.rect(screen, (80, 80, 80), (x, y, width, height))

        health_width = int(width * health / max_health)
        pygame.draw.rect(screen, (200, 30, 30), (x, y, health_width, height))