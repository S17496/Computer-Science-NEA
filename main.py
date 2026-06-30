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

        #Movement
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.gravity = 0.4
        self.jump_strength = -12
        self.on_ground = False

    def update(self):
        keys = pygame.key.get_pressed()

        #Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_d]:
            self.vel_x = self.speed

        #Vertical movement
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False
        self.vel_y += self.gravity 

        #Apply movement
        self.rect.x += self.vel_x 
        self.rect.y += self.vel_y

        # Temporary ground collision (flat floor at y=900)
        if self.rect.bottom >= 900:
            self.rect.bottom = 900
            self.vel_y = 0
            self.on_ground = True



    

player1 = Player(500, 500)
player1_group = pygame.sprite.Group(player1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0,0,150))

    player1_group.update()
    player1_group.draw(screen)

    pygame.display.update()
    # 60 FPS
    clock.tick(60)