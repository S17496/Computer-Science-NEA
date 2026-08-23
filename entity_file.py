import pygame

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

class Enemy(Entity):
    # Constructor
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)

    def movement(self) -> None:
        pass

class Zombie(Enemy):
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)
        self.__speed = 1
        