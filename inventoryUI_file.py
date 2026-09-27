import pygame
import config_file as conf

class InventoryUI:
    def __init__(self, font: pygame.font.Font) -> None:
        self.__font = font
        self.__box_width = 50
        self.__open = False

    def render_hotbar(self, screen, hotbar_items: list, selected_slot: int) -> None:

        # Draw items and boxes
        x = conf.HOTBAR_X
        y = conf.HOTBAR_Y

        for i in range(len(hotbar_items)):

            colour = (50, 50, 50)
            if i == selected_slot:
                colour = (150, 150, 150)

            self.render_box(x, y, screen, hotbar_items[i], colour)
            x += self.__box_width


    def render_box(self, x: int, y: int, screen, item, colour: tuple) -> None:

        background_box = pygame.Rect(x, y, self.__box_width, self.__box_width)
        pygame.draw.rect(screen, colour, background_box)

        item_x = x + self.__box_width // 2 - conf.ITEM_SIZE // 2
        item_y = y + self.__box_width // 2 - conf.ITEM_SIZE // 2

        if item is None:
            return 
        
        image = pygame.image.load(item.get_texture())
        screen.blit(image, (item_x, item_y))



    def render_inventory(self, screen, inventory_items: list, selected_slot: int) -> None:

        if not(self.__open):
            # For rendering ONLY hotbar
            hotbar_items = []
            for i in range(conf.HOTBAR_SIZE):
                hotbar_items.append(inventory_items[i])

            self.render_hotbar(screen, hotbar_items, selected_slot)
            return

        # Draw items and boxes
        x = conf.HOTBAR_X
        y = conf.HOTBAR_Y

        for i in range(conf.INVENTORY_SIZE // conf.HOTBAR_SIZE):
            for j in range(conf.HOTBAR_SIZE):

                item_number = i * conf.HOTBAR_SIZE + j

                colour = (50, 50, 50)
                if item_number == selected_slot:
                    colour = (150, 150, 150)

                self.render_box(x, y, screen, inventory_items[item_number], colour)

                x += self.__box_width
            y += self.__box_width
            x = conf.HOTBAR_X
        
    def change_state(self) -> None:
        self.__open = not(self.__open)