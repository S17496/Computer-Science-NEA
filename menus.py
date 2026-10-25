import pygame
import os
import json
import world
import player
import inventoryUI
import pygame_gui


class MainMenu:
    def __init__(self, screen, clock):

        self.__screen = screen
        self.__clock = clock

        self.__state = "main menu"


    def get_state(self) -> str:
        return self.__state


    def main_menu(self) -> None:

        manager = pygame_gui.UIManager(self.__screen.get_size())

        play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 250), (280, 60)), text="Play", manager=manager)        
        settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 350), (280, 60)), text="Settings", manager=manager)
        quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 450), (280, 60)), text="Quit", manager=manager)

        buttons = {play_button: self.__set_state_select_world,
                   settings_button: self.__set_state_settings,
                   quit_button: self.__set_state_quit}

        return self.__menu_logic(buttons, manager)


    def select_world_menu(self) -> world.World | None:

        manager = pygame_gui.UIManager(self.__screen.get_size())

        world_names = os.listdir("saves")

        back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1210, 550), (190, 60)), text="Back", manager=manager)
        create_world_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1210, 650), (190, 60)), text="Create world", manager=manager)

        buttons = {back_button: self.__set_state_main_menu,
                   create_world_button: self.__set_state_create_world}

        y = 200
        for world_name in world_names:
            select_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, y), (190, 60)), text=world_name, manager=manager)
            buttons[select_button] = (lambda world_name = world_name: self.__select_world(world_name))
            y += 100

        return self.__menu_logic(buttons, manager)

        
    def create_world_menu(self) -> world.World | None:

        manager = pygame_gui.UIManager(self.__screen.get_size())

        name_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1000, 250), (400, 60)), manager=manager)
        seed_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1000, 350), (400, 60)), manager=manager)
        size_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((1000, 450), (400, 60)), manager=manager)

        create_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, 550), (190, 60)), text="Create world", manager=manager)
        back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1210, 550), (190, 60)), text="Back", manager=manager)

        buttons = {create_button: lambda: self.__create_world(name_box, seed_box, size_box),
                   back_button: self.__set_state_select_world}

        return self.__menu_logic(buttons, manager)


    def select_player_menu(self) -> player.Player:

        manager = pygame_gui.UIManager(self.__screen.get_size())

        players = ["player1"]

        back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1210, 550), (190, 60)), text="Back", manager=manager)

        buttons = {back_button: self.__set_state_select_world}

        y = 200
        for player_name in players:
            select_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1000, y), (190, 60)), text=player_name, manager=manager)
            buttons[select_button] = self.__select_player
            y += 100

        return self.__menu_logic(buttons, manager)


    def __menu_logic(self, buttons: dict, manager: pygame_gui.UIManager) -> None | object:
        """Displays menu and handles button presses for the menu."""

        running = True
        
        while running:
        
            time_passed = self.__clock.tick(60) / 1000.0
        
            for event in pygame.event.get():
        
                manager.process_events(event)
        
                if event.type == pygame.QUIT:
                    self.__state = "quit"
                    running = False
        
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    return buttons[event.ui_element]()

            self.__screen.fill((30, 30, 30))
            manager.update(time_passed)
            manager.draw_ui(self.__screen)
            pygame.display.flip()


    def __select_world(self, world_name) -> world.World:

        with open(f"saves/{world_name}", "r") as file:
            save_data = json.load(file)

        self.__set_state_select_player()
        return world.World(world_name, save_data["seed"])


    def __create_world(self, name_box, seed_box, size_box) -> world.World:

        name = name_box.get_text()
        seed = int(seed_box.get_text())
        size = size_box.get_text()

        self.__set_state_select_world()

        return world.World(name, seed)


    def __select_player(self) -> player.Player:

        self.__set_state_play()

        return player.Player(0, 0, "player.png")


    def __set_state_main_menu(self) -> None:
        self.__state = "main menu"


    def __set_state_select_world(self) -> None:
        self.__state = "select world"


    def __set_state_create_world(self) -> None:
        self.__state = "create world"


    def __set_state_select_player(self) -> None:
        self.__state = "select player"


    def __set_state_settings(self) -> None:
        self.__state = "settings"


    def __set_state_quit(self) -> None:
        self.__state = "quit"


    def __set_state_play(self) -> None:
        self.__state = "play"





class GameMenu:
    def __init__(self):
        pass