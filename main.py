import pygame
import config_file as c
import world_file as w
import player_file as p

# Pygame Initialisations
pygame.init()
screen = pygame.display.set_mode((c.SCREEN_WIDTH,c.SCREEN_HEIGHT))
clock = pygame.time.Clock()

world_list = [[0,0,0,0,0,0,0,0,0,0],
         [0,0,2,1,0,0,0,2,0,0],
         [0,1,1,2,1,0,1,2,1,0],
         [1,1,1,1,1,1,1,1,1,1]]


player1 = p.Player(0, 0)
world = w.World(world_list)
font = pygame.font.Font(None, 32)

camera_x = 0
camera_y = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (int((mouse_pos[0]+camera_x)//c.TILE_SIZE), int((mouse_pos[1]+camera_y)//c.TILE_SIZE))
            if mouse_pos in world._tile_dic:
                player1.update_inventory(world._tile_dic[mouse_pos].get_name())
            world.break_tile(mouse_pos)
            

    
    
    nearby_tiles = world.get_nearby(player1.rect)
    player1.update(nearby_tiles)
    


    target_x = player1.rect.centerx - c.SCREEN_WIDTH//2
    target_y = player1.rect.centery - c.SCREEN_HEIGHT//2
    camera_x += (target_x - camera_x) * 0.1
    camera_y += (target_y - camera_y) * 0.1

    screen.fill((0,0,150))

    for tile in world._tile_group:
        screen.blit(tile.image, (tile.rect.x - camera_x, tile.rect.y - camera_y))
    
    
    screen.blit(player1.image, (player1.rect.x - camera_x, player1.rect.y - camera_y))

    screen.blit(font.render("hi", True, (255, 255, 255)), (10, 10))
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)