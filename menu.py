import pygame
import world
import player
import inventoryUI
import pygame_gui

class Menu:
    def __init__(self, screen, clock):

        self.screen = screen
        self.clock = clock

        self.__state = "main menu"


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


    def select_world(self) -> world.World:
        # Load worlds
        manager = pygame_gui.UIManager(self.screen.get_size())

        worlds = ["world1"]

        world_buttons = []

        back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1210, 550), (190, 60)), text="Back", manager=manager)

        y = 200
        for world_name in worlds:
            select_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, y), (190, 60)), text=world_name, manager=manager)
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
                            return world.World("world1", 0)
        
                    if event.ui_element == back_button:
                        self.__state = "main menu"
                        running = False

            self.screen.fill((30, 30, 30))
            manager.update(time_passed)
            manager.draw_ui(self.screen)
            pygame.display.flip()
            
        


    def create_world(self) -> world.World | None:

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
        self.__state = "play"
        return player.Player(500, 0, "player.png")
    