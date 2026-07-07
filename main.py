import pygame

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TILE_SIZE = 128


# Pygame Initialisations
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()

world = [[0,0,0,0,0,0,0,0,0,0],
         [0,0,1,1,0,0,0,1,0,0],
         [0,1,1,1,1,0,1,1,1,0],
         [1,1,1,1,1,1,1,1,1,1]]

class Player(pygame.sprite.Sprite):
    # Constructor
    def __init__(self,x,y):
        super().__init__()
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
                                
class Tile(pygame.sprite.Sprite):
    # Constructor
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((100, 200, 100))
        self.rect = self.image.get_rect(topleft=(x,y))



player1 = Player(0, 0)

tile_group = pygame.sprite.Group()
for row_index, row in enumerate(world):
    for col_index, tile in enumerate(row):
        if tile == 1:
            tile_group.add(Tile(col_index * TILE_SIZE, row_index * TILE_SIZE))


camera_x = 0
camera_y = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    
    player1.update(tile_group)
    


    target_x = player1.rect.centerx - SCREEN_WIDTH//2
    target_y = player1.rect.centery - SCREEN_HEIGHT//2
    camera_x += (target_x - camera_x) * 0.1
    camera_y += (target_y - camera_y) * 0.1

    screen.fill((0,0,150))

    for tile in tile_group:
        screen.blit(tile.image, (tile.rect.x - camera_x, tile.rect.y - camera_y))
    
    
    screen.blit(player1.image, (player1.rect.x - camera_x, player1.rect.y - camera_y))
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)