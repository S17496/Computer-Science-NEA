import pygame
import config_file as c
import world_file as w
import player_file as p

# Pygame Initialisations
pygame.init()
screen = pygame.display.set_mode((c.SCREEN_WIDTH,c.SCREEN_HEIGHT))
clock = pygame.time.Clock()


# Creating objects
noise1d = w.PerlinNoise(0)
player1 = p.Player(0, 0)
world = w.World(noise1d)
font = pygame.font.Font(None, 32)
inventory_ui = p.InventoryUI(font)

# Starting camera coordinates
camera_x = 0
camera_y = 0

# Main loop
running = True
while running:
    for event in pygame.event.get():
        # User quits
        if event.type == pygame.QUIT:
            running = False

        # Breaking a tile
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (int((mouse_pos[0]+camera_x)//c.TILE_SIZE), int((mouse_pos[1]+camera_y)//c.TILE_SIZE))
            if mouse_pos in world._tile_dic:
                player1.update_inventory(p.Item(world._tile_dic[mouse_pos].get_name(), 1, 9999))
            world.break_tile(mouse_pos)

        # Switching slot
        elif event.type == pygame.KEYDOWN:
            if event.key in [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]:            
                slot_num = (event.key - 39) % 10
                print(slot_num)
                player1.get_inventory().set_selected_slot(slot_num)


    # Allows only nearby tiles to be checked for collisions
    nearby_tiles = world.get_nearby(player1.rect)
    player1.update(nearby_tiles)
    

    # Camera movement
    target_x = player1.rect.centerx - c.SCREEN_WIDTH//2
    target_y = player1.rect.centery - c.SCREEN_HEIGHT//2
    camera_x += (target_x - camera_x) * 0.1
    camera_y += (target_y - camera_y) * 0.1

    # Drawing
    screen.fill((0,0,150))

    for tile in world._tile_group:
        screen.blit(tile.get_texture(), (tile.rect.x - camera_x, tile.rect.y - camera_y))
    
    
    screen.blit(player1.image, (player1.rect.x - camera_x, player1.rect.y - camera_y))

    inventory_ui.render_hotbar(screen, player1.get_inventory().get_items()[0:c.HOTBAR_SIZE], player1.get_inventory().get_selected_slot())
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)