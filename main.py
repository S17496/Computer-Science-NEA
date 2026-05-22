import pygame

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Pygame Initialisations
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 200, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
    

player1 = Player(500, 500)
player1_group = pygame.sprite.Group(player1)

running = True
while running:
    screen.fill((0,0,150))
    player1_group.draw(screen)
    # 60 FPS
    clock.tick(60)