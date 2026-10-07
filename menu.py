import world_file as w
import pygame
import config_file as conf
import camera_file as camera
import events
import inventoryUI_file as invUI

pygame.init()

class Button:
    def __init__(self, text, rect):
        self.__text = text
        self.rect = pygame.Rect(rect)

        self.__normal_color = (80, 80, 80)
        self.__hover_color = (120, 120, 120)
        self.__text_color = (255, 255, 255)

        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            color = self.__hover_color
        else:
            color = self.__normal_color

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        text_surface = self.font.render(self.__text, True, self.__text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)

        surface.blit(text_surface, text_rect)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    return True

        return False

    
class Menu:
    def __init__(self, screen):
        self.__state = "main menu"
        self.screen = screen
        self.__saved_worlds = []
        self.__saved_players = []

    def get_state(self) -> str:
        return self.__state

    def main_menu(self) -> None:

        buttons = (Button("Play", (1000, 250, 280, 60)), Button("Settings", (1000, 350, 280, 60)), Button("Quit", (1000, 450, 280, 60)))

        running = True
        while running:

            selected_button = None 

            for button in buttons:
                button.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:

                        if buttons[0].handle_event(event):
                            selected_button = "play"

                        elif buttons[1].handle_event(event):
                            selected_button = "settings"

                        elif buttons[2].handle_event(event):
                            selected_button = "quit"

            if selected_button == "play":
                self.__state = "select world"
                running = False

            elif selected_button == "settings":
                self.__state = "settings"
                running = False

            elif selected_button == "quit":
                self.__state = "quit"
                running = False

            pygame.display.flip()
        

    def select_world(self) -> w.World | None:
        name = input()
        seed = input()
        size = input()
        back = input()

        if back == "Yes":
            self.__state = "Main menu"
            return

        self.__state = "select character"
        return w.World(seed)


class Game:
    def __init__(self):
        self.__world = None
        self.__player = None
        self.__camera = camera.Camera()
        self.__inventory_ui = invUI.InventoryUI(pygame.font.Font(None, 32))
        self.screen = pygame.display.set_mode((conf.SCREEN_WIDTH, conf.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.__menu = Menu(self.screen)
        self.run()
        

    def run(self):

        menu_state = self.__menu.get_state()

        if menu_state == "main menu":
            self.__menu.main_menu()
            self.run()

        elif menu_state == "select world":
            self.__world = self.__menu.select_world()
            self.run()

        elif menu_state == "select player":
            self.__player = self.__menu.select_player()
            self.run()

        elif menu_state == "play" and  self.__player is not None and self.__world is not None:
            self.__event_handler = events.EventHandler(self.__player, self.__world, self.__camera, drop_tile, inventory_ui)
            self.play()
            self.run()

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
