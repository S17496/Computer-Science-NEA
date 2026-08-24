import pygame
import config_file as conf
import world_file as w
import player_file as p
import camera_file as cam
import inventory_file as inv
import inventoryUI_file as invUI
import items_file as items

def handle_slot_switching(event, player: p.Player) -> None:
    slot_num = (event.key - 39) % 10
    player.get_inventory().set_selected_slot(slot_num)
    

def handle_key_event(event, player: p.Player) -> None:
    if event.key in [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]:
        handle_slot_switching(event, player)

def handle_left_click(player: p.Player) -> None:
    global breakstart, break_target
    # Breaking blocks

    if isinstance(player.get_inventory().get_selected_item(), items.Pickaxe):
        break_time = int(2000/player.get_inventory().get_selected_item().get_pickaxe_speed())
        mouse_pos = pygame.mouse.get_pos()
        tile_pos = (int((mouse_pos[0]+camera.get_x())//conf.TILE_SIZE), int((mouse_pos[1]+camera.get_y())//conf.TILE_SIZE))
        if tile_pos in world._tile_dic:
            if breakstart == None:
                breakstart = pygame.time.get_ticks()
                break_target = tile_pos
    
            elapsed = pygame.time.get_ticks() - breakstart
    
            if tile_pos != break_target:
                breakstart = None
                break_target = None 
    
            if elapsed >= break_time and break_target != None:
                tile_item_entity = world._tile_dic[tile_pos].drop_tile(items.Item(world._tile_dic[tile_pos].get_item_id(), 1))
                item_entities.add(tile_item_entity)
                world.break_tile(tile_pos)
                breakstart = None
                break_target = None
    
    elif isinstance(player.get_inventory().get_selected_item(), p.TileItem):
        mouse_pos = pygame.mouse.get_pos()
        tile_pos = (int((mouse_pos[0]+camera.get_x())//conf.TILE_SIZE), int((mouse_pos[1]+camera.get_y())//conf.TILE_SIZE))
        if tile_pos not in world._tile_dic:
            # PLACE BLOCK CODE
            item = player.get_inventory().get_selected_item()
            item.set_quantity(item.get_quantity()-1)
    


def handle_events(player) -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            handle_key_event(event, player)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pass
        elif pygame.mouse.get_pressed()[0]:
            handle_left_click(player)
    return True

# Pygame Initialisations
pygame.init()
screen = pygame.display.set_mode((conf.SCREEN_WIDTH,conf.SCREEN_HEIGHT))
clock = pygame.time.Clock()


# Creating objects
noise1d = w.PerlinNoise(0)
player1 = p.Player(conf.TILE_SIZE * 500, 0, "player.png")
world = w.World(noise1d)
font = pygame.font.Font(None, 32)
inventory_ui = invUI.InventoryUI(font)
camera = cam.Camera()
item_entities = pygame.sprite.Group()

# Temporary pickaxe giver
player1.get_inventory().add_item(items.Pickaxe("100", 1))

# Variable used for breaking blocks
breakstart = None 

# Main loop
running = True
while running:
    running = handle_events(player1)


    # Allows only nearby tiles to be checked for collisions
    nearby_tiles = world.get_nearby_rects(player1.rect, 10, 10)
    player1.update(nearby_tiles)
    

    # Camera movement
    camera.move_camera(player1.rect.centerx - conf.SCREEN_WIDTH//2, player1.rect.centery - conf.SCREEN_HEIGHT//2)

    # Draw background
    screen.fill((0,0,150))

    # Draw item_entities
    for item_entity in item_entities:
        screen.blit(item_entity.image, (item_entity.rect.x - camera.get_x(), item_entity.rect.y - camera.get_y()))

    # Draw tiles
    tiles_to_draw = world.get_nearby(player1.rect, conf.SCREEN_WIDTH // conf.TILE_SIZE, conf.SCREEN_HEIGHT // conf.TILE_SIZE)
    for tile in tiles_to_draw:
        screen.blit(tile.image, (tile.rect.x - camera.get_x(), tile.rect.y - camera.get_y()))
    
    # Draw player
    screen.blit(player1.image, (player1.rect.x - camera.get_x(), player1.rect.y - camera.get_y()))

    # Draw hotbar
    inventory_ui.render_hotbar(screen, player1.get_inventory().get_items()[0:conf.HOTBAR_SIZE], player1.get_inventory().get_selected_slot())
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)