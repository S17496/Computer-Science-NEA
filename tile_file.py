import pygame
import config_file as c

class Tile(pygame.sprite.Sprite):
    # Constructor
    def __init__(self,x,y):
        super().__init__()

        # Pygame convention for sprites. Attributes kept public.
        self.image = pygame.Surface((c.TILE_SIZE, c.TILE_SIZE))
        self.image.fill((100, 200, 100))
        self.rect = self.image.get_rect(topleft=(x,y))