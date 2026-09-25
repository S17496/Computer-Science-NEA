import pygame
import config_file as conf
import world_file as w
import player_file as p
import camera_file as cam
import inventoryUI_file as invUI
import items_file as items
import entity_file as ent
import events
import json

with open("item_data.json", "r") as tile_data:
    tile_data = json.load(tile_data)

def drop_tile(tile_coordinates, item_id):
    tile_item_entity = ent.ItemEntity(
        tile_coordinates[0] * conf.TILE_SIZE,
        tile_coordinates[1] * conf.TILE_SIZE,
        tile_data[item_id]["dropped_texture"],
        items.TileItem(item_id, 1)
    )
    item_entities.add(tile_item_entity)

# Pygame initialisations
pygame.init()
screen = pygame.display.set_mode((conf.SCREEN_WIDTH, conf.SCREEN_HEIGHT))
clock = pygame.time.Clock()


# Creating objects
player = p.Player(conf.TILE_SIZE * 500, 0, "player.png")
world = w.World(2)
font = pygame.font.Font(None, 32)
inventory_ui = invUI.InventoryUI(font)
camera = cam.Camera()
item_entities = pygame.sprite.Group()
event_handler = events.EventHandler(player, world, camera, drop_tile)

# Temporary pickaxe giver
player.get_inventory().add_item(items.Pickaxe("100", 1))

# Variables used for breaking blocks
breakstart = None 
break_target = None

# Main loop
running = True
while running:
    running = event_handler.handle_events()


    # Player logic
    nearby_tiles = world.get_nearby_rects(player.rect, 10, 10)
    player.update(nearby_tiles, item_entities)

    # Dropped item logic
    for dropped_item in item_entities:
        nearby_tiles = world.get_nearby_rects(dropped_item.rect, 10, 10)
        dropped_item.update(nearby_tiles, item_entities)

    # Camera movement
    camera.move_camera(player.rect.centerx - conf.SCREEN_WIDTH//2, player.rect.centery - conf.SCREEN_HEIGHT//2)

    # Draw background
    screen.fill((0,0,150))

    # Draw item_entities
    for item_entity in item_entities:
        screen.blit(item_entity.image, (item_entity.rect.x - camera.get_x(), item_entity.rect.y - camera.get_y()))

    # Draw tiles
    world.render_world(player.rect, screen, camera)

    # Draw player
    screen.blit(player.image, (player.rect.x - camera.get_x(), player.rect.y - camera.get_y()))

    # Draw hotbar
    inventory_ui.render_hotbar(screen, player.get_inventory().get_items()[0:conf.HOTBAR_SIZE], player.get_inventory().get_selected_slot())
   
    pygame.display.update()
    # 60 FPS
    clock.tick(60)