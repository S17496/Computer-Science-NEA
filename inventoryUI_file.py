import pygame
import config_file as conf

class InventoryUI:
    def __init__(self, font: pygame.font.Font) -> None:
        self.__font = font
        self.__box_width = 50
        self.__open = False

    def render_hotbar(self, screen, hotbar_items: list, selected_slot: int) -> None:
        # Draw background box
        background_box = pygame.Rect(200, 200, conf.HOTBAR_SIZE * (self.__box_width + 20), self.__box_width)
        pygame.draw.rect(screen, (50, 50, 50), background_box)

        # Draw items
        x = 210
        for item in hotbar_items:
            if item != None:
                text_surface = self.__font.render(f"{item.get_name()}: {item.get_quantity()}", True, (255, 255, 255))
                screen.blit(text_surface, (x, 200))
            x += int(self.__box_width * 1.1)

        # Draw selected slot
        border = pygame.Rect(210 + selected_slot * (self.__box_width + 20), 200, 10, 10)
        pygame.draw.rect(screen, (255, 255, 255), border)

    def render_inventory(self, inventory_items: list, selected_slot: int) -> None:

        hotbar_items = []
        for i in range(conf.HOTBAR_SIZE):
            hotbar_items.append(inventory_items[i])

        if not(open):
            return 

        
