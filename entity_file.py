import pygame
import inventory_file as inv

class Entity(pygame.sprite.Sprite):
    # Constructor
        def __init__(self, x: int, y: int, image: str) -> None:
            super().__init__()
            # Pygame convention for sprites. Attributes kept public.
            self.image = pygame.image.load(image)
            self.rect = self.image.get_rect(topleft=(x, y))


class ItemEntity(Entity):
    def __init__(self, x: int, y: int, image: str, item: inv.Item) -> None:
        super().__init__(x, y, image)
        self.__item = item

