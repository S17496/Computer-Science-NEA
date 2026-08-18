import pygame
import config_file as c
import world_file as w
import player_file as p
import camera_file as cam

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
camera = cam.Camera()

# Temporary pickaxe giver
player1.get_inventory().add_item(p.Pickaxe("Copper pickaxe", 1, 1, 1, 1))

# Variable used for timing tile breaking
breakstart = None

# Main loop
running = True
while running:
    for event in pygame.event.get():
        # User quits
        if event.type == pygame.QUIT:
            running = False

        # Breaking a tile
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if isinstance(player1.get_inventory().get_selected_item(), p.Pickaxe):
                break_time = int(2000/player1.get_inventory().get_selected_item().get_speed())
                mouse_pos = pygame.mouse.get_pos()
                tile_pos = (int((mouse_pos[0]+camera.get_x())//c.TILE_SIZE), int((mouse_pos[1]+camera.get_y())//c.TILE_SIZE))
                if tile_pos in world._tile_dic:
                    if breakstart == None:
                        breakstart = pygame.time.get_ticks()

                    elapsed = pygame.time.get_ticks() - breakstart

                    if elapsed >= break_time:
                        player1.update_inventory(p.Item(world._tile_dic[mouse_pos].get_name(), 1, 9999))
                        world.break_tile(mouse_pos)
                        breakstart = None
                else:
                    breakstart = None

            


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
    camera.move_camera(player1.rect.centerx - c.SCREEN_WIDTH//2, player1.rect.centery - c.SCREEN_HEIGHT//2)

    # Drawing
    screen.fill((0,0,150))

    for tile in world._tile_group:
        screen.blit(tile.get_texture(), (tile.rect.x - camera.get_x(), tile.rect.y - camera.get_y()))
    
    
    screen.blit(player1.image, (player1.rect.x - camera.get_x(), player1.rect.y - camera.get_y()))

    inventory_ui.render_hotbar(screen, player1.get_inventory().get_items()[0:c.HOTBAR_SIZE], player1.get_inventory().get_selected_slot())
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)