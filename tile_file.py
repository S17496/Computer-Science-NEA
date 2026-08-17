import pygame
import config_file as c

tile_properties = {0: ["air", (255, 255, 255), 0],
                   1: ["dirt", "dirt.png", 10],
                   2: ["stone", (0, 200, 0), 20]}

class Tile(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, x: int, y: int, id) -> None:
        super().__init__()

        # Block properties
        self.__id = id
        self.__name = tile_properties[self.__id][0]
        self.__texture = pygame.image.load(tile_properties[self.__id][1]).convert_alpha()
        self.__hardness = tile_properties[self.__id][2]

        # Pygame convention for sprites. Attributes kept public.
        self.image = pygame.Surface((c.TILE_SIZE, c.TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x,y))

    

    # Getters and setters
    def get_id(self) -> int:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_hardness(self) -> int:
        return self.__hardness

    def get_texture(self) -> int:
            return self.__texture
    