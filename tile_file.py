import pygame
import config_file as conf
import entity_file as ent
import json


class Tile(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, x: int, y: int, id) -> None:
        super().__init__()

        with open("tile_data.json", "r") as file:
            tile_data = json.load(file)[id]

        # Tile properties

        self.__item_id = tile_data["drops"]["item_id"]
        self.__name = tile_data["name"]
        self.__hardness = tile_data["hardness"]

        # Pygame convention for sprites. Attributes kept public.

        self.image = pygame.image.load(tile_data["texture"])
        self.rect = self.image.get_rect(topleft=(x,y))

    def drop_tile(self, item) -> ent.ItemEntity:
        with open("item_data.json", "r") as file:
            image = json.load(file)[self.__item_id]["dropped_texture"]
        return ent.ItemEntity(self.rect.x, self.rect.y, image, item)
    

    # Getters and setters
    def get_item_id(self) -> str:
        return self.__item_id

    def get_name(self) -> str:
        return self.__name

    def get_hardness(self) -> int:
        return self.__hardness

    