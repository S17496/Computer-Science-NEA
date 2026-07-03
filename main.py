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

        #Apply horizontal movement
        self.rect.x += self.vel_x 
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vel_x > 0:
                    self.rect.right = tile.left
                elif self.vel_x < 0:
                    self.rect.left = tile.right  

        #Apply vertical movement
        self.rect.y += self.vel_y
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.vel_y > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0
                                

        # Temporary ground collision (flat floor at y=900)
        if self.rect.bottom >= 128*4:
            self.rect.bottom = 128*4
            self.vel_y = 0
            self.on_ground = True


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


    camera_x = player1.rect.centerx - SCREEN_WIDTH//2
    camera_y = player1.rect.centery - SCREEN_HEIGHT//2

    screen.fill((0,0,150))

    for tile in tiles:
            pygame.draw.rect(screen,(100,200,100),(tile.x - camera_x, tile.y - camera_y, TILE_SIZE, TILE_SIZE))
    
    






    screen.blit(player1.image, (player1.rect.x - camera_x, player1.rect.y - camera_y))
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)