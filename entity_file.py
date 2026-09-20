import pygame
import random 
import config_file as conf

class Entity(pygame.sprite.Sprite):
    # Constructor
        def __init__(self, x: int, y: int, image: str) -> None:
            super().__init__()

            # Pygame convention for sprites. Attributes kept public.
            self.image = pygame.image.load(image)
            self.rect = self.image.get_rect(topleft=(x, y))


class ItemEntity(Entity):
    # Constructor
    def __init__(self, x: int, y: int, image: str, item) -> None:
        super().__init__(x, y, image)
        self.__item = item
        self.__vel_y = 0
        self.__gravity = conf.GRAVITY

    def get_item(self) -> object:
        return self.__item

    def update(self, tiles):

        # Apply vertical movement
        self.rect.y += self.__vel_y
        self.__vel_y += self.__gravity 

        # Collisions
        for rect in tiles:
            if self.rect.colliderect(rect):
                if self.__vel_y > 0:
                    self.rect.bottom = rect.top
                    self.__vel_y = 0
                elif self.__vel_y < 0:
                    self.rect.top = rect.bottom
                    self.__vel_y = 0


    

class Enemy(Entity):
    # Constructor
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)

    def movement(self) -> None:
        return

class Zombie(Enemy):
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)
        self.__speed = 1
        