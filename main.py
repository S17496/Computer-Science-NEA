import pygame

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Pygame Initialisations
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()

running = True
while running:
    screen.fill((0,0,150))
    
    # 60 FPS
    clock.tick(60)