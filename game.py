import pygame
import config
import world
import player
import camera
import inventoryUI
import items
import entities
import events
import json
import menu

class Game:
    def __init__(self):

        self.__screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.__clock = pygame.time.Clock()

        self.__world = None
        self.__player = None
        self.__item_entities = pygame.sprite.Group()
        self.__event_handler = None
        self.__camera = camera.Camera()
        self.__inventory_ui = inventoryUI.InventoryUI(pygame.font.Font(None, 32))
        self.__menu = menu.Menu(self.__screen, self.__clock)
        

    def run(self):

        while True:
            menu_state = self.__menu.get_state()

            if menu_state == "main menu":
                self.__menu.main_menu()

            elif menu_state == "create world":
                self.__world = self.__menu.create_world()

            elif menu_state == "select world":
                self.__world = self.__menu.select_world()

            elif menu_state == "select player":
                self.__player = self.__menu.select_player()

            elif menu_state == "play" and self.__player is not None and self.__world is not None:
                self.__event_handler = events.EventHandler(self.__player, self.__world, self.__camera, self.drop_tile, self.drop_item, self.__inventory_ui)
                self.play()
                return

            else:
                return


    def play(self) -> None:

        self.__world.update(self.__player.rect, config.LOAD_DISTANCE ** 2)

        running = True
        while running:

            running = self.__event_handler.handle_events()

            # Update objects

            self.__world.update(self.__player.rect)

            nearby_tiles = self.__world.get_nearby_rects(self.__player.rect, 10, 10)
            self.__player.update(nearby_tiles, self.__item_entities)

            for dropped_item in self.__item_entities:
                nearby_tiles = self.__world.get_nearby_rects(dropped_item.rect, 2, 3)
                dropped_item.update(nearby_tiles, self.__item_entities)

            # Camera movement
            self.__camera.move_camera(self.__player.rect.centerx - config.SCREEN_WIDTH//2, self.__player.rect.centery - config.SCREEN_HEIGHT//2)

            # Draw background
            self.__screen.fill((0,0,150))

            # Draw item_entities
            for item_entity in self.__item_entities:
                self.__screen.blit(item_entity.image, (item_entity.rect.x - self.__camera.get_x(), item_entity.rect.y - self.__camera.get_y()))

            

            self.__world.render_world(self.__player.rect, self.__screen, self.__camera)

            self.__screen.blit(self.__player.image, (self.__player.rect.x - self.__camera.get_x(), self.__player.rect.y - self.__camera.get_y()))

            self.__inventory_ui.render_inventory(self.__screen, self.__player.get_inventory().get_items(), self.__player.get_inventory().get_selected_slot())
            self.__inventory_ui.render_hand_item(self.__screen, self.__player.get_hand())
        
            pygame.display.update()

            # 60 FPS
            self.__clock.tick(60)


    def drop_tile(self, tile_coordinates: tuple, item_id: str) -> None:

        with open("data/items.json", "r") as tile_data:
            tile_data = json.load(tile_data)

        tile_item_entity = entities.ItemEntity(tile_coordinates[0] * config.TILE_SIZE,tile_coordinates[1] * config.TILE_SIZE,tile_data[item_id]["texture"],items.TileItem(item_id, 1))
        self.__item_entities.add(tile_item_entity)


    def drop_item(self, x: int, y: int, item: items.Item) -> None:
        
        item_entity = entities.ItemEntity(x, y, item.get_texture(), item)
        self.__item_entities.add(item_entity)
