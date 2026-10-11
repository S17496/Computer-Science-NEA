import world_file as w
import pygame
import config_file as conf
import camera_file as camera
import events
import inventoryUI_file as invUI
import pygame_gui

pygame.init()



class Menu:
    def __init__(self, screen, clock):

        self.screen = screen
        self.clock = clock

        self.__state = "main menu"
        self.__saved_worlds = []
        self.__saved_players = []


    def get_state(self) -> str:
        return self.__state


    def main_menu(self) -> None:

        manager = pygame_gui.UIManager(self.screen.get_size())

        play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 250), (280, 60)), text="Play", manager=manager)        
        settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 350), (280, 60)), text="Settings", manager=manager)
        quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 450), (280, 60)), text="Quit", manager=manager)
                
        running = True

        while running:

            time_passed = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():

                manager.process_events(event)

                if event.type == pygame.QUIT:
                    self.__state = "quit"
                    running = False

                elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                    if event.ui_element == play_button:
                        self.__state = "select world"
                        running = False

                    elif event.ui_element == settings_button:
                        self.__state = "settings"
                        running = False

                    elif event.ui_element == quit_button:
                        self.__state = "quit"
                        running = False

                self.screen.fill((30, 30, 30))
                manager.update(time_passed)
                manager.draw_ui(self.screen)
                pygame.display.flip()


    def select_world(self) -> w.World:
        # Load worlds
        manager = pygame_gui.UIManager(self.screen.get_size())

        worlds = ["world1"]

        world_buttons = []

        back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1210, 550), (190, 60)), text="Back", manager=manager)

        y = 200
        for world_name in worlds:
            select_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, y), (190, 60)), text="Select world", manager=manager)
            world_buttons.append((select_button, world_name))
            y += 100

        running = True
        
        while running:
        
            time_passed = self.clock.tick(60) / 1000.0
        
            for event in pygame.event.get():
        
                manager.process_events(event)
        
                if event.type == pygame.QUIT:
                    self.__state = "quit"
                    running = False
        
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                    for button, world_name in world_buttons:
                        if event.ui_element == button:

                            self.__state = "select player"

                            # TEMPORARY
                            return w.World(0)
        
                    if event.ui_element == back_button:
                        self.__state = "main menu"
                        running = False

            self.screen.fill((30, 30, 30))
            manager.update(time_passed)
            manager.draw_ui(self.screen)
            pygame.display.flip()
            
        


    def create_world(self) -> w.World | None:

        manager = pygame_gui.UIManager(self.screen.get_size())

        create_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 550), (190, 60)), text="Create world", manager=manager)
        back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1210, 550), (190, 60)), text="Back", manager=manager)

        name_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1000, 250), (400, 60)), manager=manager)
        seed_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1000, 350), (400, 60)), manager=manager)
        size_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1000, 450), (400, 60)), manager=manager)

        running = True

        while running:

            time_passed = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():

                manager.process_events(event)

                if event.type == pygame.QUIT:
                    self.__state = "quit"
                    running = False

                elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                    if event.ui_element == create_button:

                        world_name = name_box.get_text()
                        seed_text = seed_box.get_text()
                        size_text = size_box.get_text()

                        self.__state = "select world"
                        running = False

                    elif event.ui_element == back_button:
                        self.__state = "main menu"
                        running = False


                self.screen.fill((30, 30, 30))
                manager.update(time_passed)
                manager.draw_ui(self.screen)
                pygame.display.flip()


    def select_player(self) -> player.Player:
        pass

class Game:
    def __init__(self):

        self.screen = pygame.display.set_mode((conf.SCREEN_WIDTH, conf.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.__world = None
        self.__player = None
        self.__camera = camera.Camera()
        self.__inventory_ui = invUI.InventoryUI(pygame.font.Font(None, 32))
        self.__menu = Menu(self.screen, self.clock)
        self.run()
        

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
                self.__event_handler = events.EventHandler(self.__player, self.__world, self.__camera, drop_tile, inventory_ui,)
                self.play()

            else:
                return


    def play(self) -> None:

        running = True
        while running:
            running = event_handler.handle_events()

            world.queue_nearby_chunks(player.rect, conf.RENDER_DISTANCE, conf.RENDER_DISTANCE)
            world.process_chunk_queue(1)

            nearby_tiles = world.get_nearby_rects(player.rect, 10, 10)
            player.update(nearby_tiles, item_entities)

            # Dropped item logic
            for dropped_item in item_entities:
                nearby_tiles = world.get_nearby_rects(dropped_item.rect, 2, 3)
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
            world.unload_far_chunks(player.rect)

            # Draw player
            screen.blit(player.image, (player.rect.x - camera.get_x(), player.rect.y - camera.get_y()))

            # Draw hotbar
            inventory_ui.render_inventory(screen, player.get_inventory().get_items(), player.get_inventory().get_selected_slot())
        
            pygame.display.update()
            # 60 FPS
            clock.tick(60)

Game()
