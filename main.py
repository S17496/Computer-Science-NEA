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
    #Constructor
    def __init__(self,x,y):
        super().__init__()
        self.__image = pygame.Surface((40, 60))
        self.__image.fill((255, 200, 0))
        self.__rect = self.__image.get_rect(topleft=(x, y))

        #Movement
        self.__vel_x = 0
        self.__vel_y = 0
        self.__speed = 5
        self.__gravity = 0.4
        self.__jump_strength = -12
        self.__on_ground = False

    def update(self):
        keys = pygame.key.get_pressed()

        #Horizontal movement
        self.__vel_x = 0
        if keys[pygame.K_a]:
            self.__vel_x = -self.__speed
        if keys[pygame.K_d]:
            self.__vel_x = self.__speed

        #Vertical movement
        if keys[pygame.K_SPACE] and self.__on_ground:
            self.__vel_y = self.__jump_strength
            self.__on_ground = False
        self.__vel_y += self.__gravity
        self.__on_ground = False

        #Apply horizontal movement
        self.__rect.x += self.__vel_x 

        #Horizontal collisions
        for tile in tiles:
            if self.__rect.colliderect(tile):
                if self.__vel_x > 0:
                    self.__rect.right = tile.left
                elif self.__vel_x < 0:
                    self.__rect.left = tile.right  

        #Apply vertical movement
        self.__rect.y += self.__vel_y
        
        #Vertical collisions
        for tile in tiles:
            if self.__rect.colliderect(tile):
                if self.__vel_y > 0:
                    self.__rect.bottom = tile.top
                    self.__vel_y = 0
                    self.__on_ground = True
                elif self.__vel_y < 0:
                    self.__rect.top = tile.bottom
                    self.__vel_y = 0
                                

        # Temporary ground collision (flat floor at y=900)
        if self.__rect.bottom >= 128*4:
            self.__rect.bottom = 128*4
            self.__vel_y = 0
            self.__on_ground = True
        
        # Getters
    def get_rect(self):
        return self.__rect

    def get_image(self):
            return self.__image
    

class Tile(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()



player1 = Player(0, 0)

tiles = []
for row_index, row in enumerate(world):
    for col_index, tile in enumerate(row):
        if tile == 1:
            rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tiles.append(rect)



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    
    player1.update()

    player_rect = player1.get_rect()
    camera_x = player_rect.centerx - SCREEN_WIDTH//2
    camera_y = player_rect.centery - SCREEN_HEIGHT//2

    screen.fill((0,0,150))

    for tile in tiles:
            pygame.draw.rect(screen,(100,200,100),(tile.x - camera_x, tile.y - camera_y, TILE_SIZE, TILE_SIZE))
    
    
    screen.blit(player1.get_image(), (player_rect.x - camera_x, player_rect.y - camera_y))
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)