import pygame
import config_file as c
import world_file as w

# Pygame Initialisations
pygame.init()
screen = pygame.display.set_mode((c.SCREEN_WIDTH,c.SCREEN_HEIGHT))
clock = pygame.time.Clock()

world_list = [[0,0,0,0,0,0,0,0,0,0],
         [0,0,1,1,0,0,0,1,0,0],
         [0,1,1,1,1,0,1,1,1,0],
         [1,1,1,1,1,1,1,1,1,1]]

class Player(pygame.sprite.Sprite):
    # Constructor
    def __init__(self,x,y):
        super().__init__()

        # Pygame convention for sprites. Attributes kept public.
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 200, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movement
        self.__vel_x = 0
        self.__vel_y = 0
        self.__speed = 5
        self.__gravity = 0.4
        self.__jump_strength = -12
        self.__on_ground = False

    def update(self, tiles):
        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.__vel_x = 0
        if keys[pygame.K_a]:
            self.__vel_x = -self.__speed
        if keys[pygame.K_d]:
            self.__vel_x = self.__speed

        #Vertical movement
        if keys[pygame.K_SPACE] and self.__on_ground:
            self.__vel_y = self.__jump_strength
        self.__vel_y += self.__gravity
        self.__on_ground = False

        # Apply horizontal movement
        self.rect.x += self.__vel_x 

        # Horizontal collisions
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.__vel_x > 0:
                    self.rect.right = tile.rect.left
                elif self.__vel_x < 0:
                    self.rect.left = tile.rect.right  

        # Apply vertical movement
        self.rect.y += self.__vel_y
        
        # Vertical collisions
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.__vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.__vel_y = 0
                    self.__on_ground = True
                elif self.__vel_y < 0:
                    self.rect.top = tile.rect.bottom
                    self.__vel_y = 0
                                


player1 = Player(0, 0)
world_obj = w.World(world_list)

camera_x = 0
camera_y = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    
    player1.update(world_obj.tile_group)
    


    target_x = player1.rect.centerx - c.SCREEN_WIDTH//2
    target_y = player1.rect.centery - c.SCREEN_HEIGHT//2
    camera_x += (target_x - camera_x) * 0.1
    camera_y += (target_y - camera_y) * 0.1

    screen.fill((0,0,150))

    for tile in world_obj.tile_group:
        screen.blit(tile.image, (tile.rect.x - camera_x, tile.rect.y - camera_y))
    
    
    screen.blit(player1.image, (player1.rect.x - camera_x, player1.rect.y - camera_y))
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)