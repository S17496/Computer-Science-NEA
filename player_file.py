import pygame
import config_file as c


class Item:
    def __init__(self, name: str, quantity: int, max_stack: int) -> None:
        self._name = name
        self._quantity = quantity 
        self._max_stack = max_stack

    # Getters and setters
    def get_name(self) -> str:
        return self._name

    def get_quantity(self) -> int:
        return self._quantity

    def get_max_stack(self) -> int:
        return self._max_stack

    def set_quantity(self, quantity: str) -> None:
        self._quantity = quantity


class InventoryUI:
    def __init__(self, font: pygame.font.Font) -> None:
        self.__font = font
        self.__box_width = 100

    def render(self, screen, inventory_items: list) -> None:
        # Draw background box
        background_box = pygame.Rect(200, 200, c.HOTBAR_SIZE * (self.__box_width + 20), 100)
        pygame.draw.rect(screen, (50, 50, 50), background_box)

        # Draw items
        x = 210
        for item in inventory_items:
            if item != None:
                text_surface = self.__font.render(f"{item.get_name()}: {item.get_quantity()}", True, (255, 255, 255))
                screen.blit(text_surface, (x, 200))
            x += self.__box_width + 20

class Inventory:
    def __init__(self) -> None:
        self.__selected_slot = 0
        
        # Fills in all inventory slots with placeholder None
        self.__items = []
        for _ in range(c.INVENTORY_SIZE):
            self.__items.append(None)


    # Getters and setters
    def get_items(self) -> list:
        return self.__items

    def add_item(self, item: Item) -> None:
        for i in range(c.INVENTORY_SIZE):
            if self.__items[i] != None:
                if item.get_name() == self.__items[i].get_name() and self.__items[i].get_quantity() < self.__items[i].get_max_stack():
                    self.__items[i].set_quantity(self.__items[i].get_quantity() + 1)
                    break
        else:
            for i in range(c.INVENTORY_SIZE):
                if self.__items[i] == None:
                    self.__items[i] = item
                    break

    def get_selected_slot(self) -> int:
        return self.__selected_slot

    def set_selected_slot(self, slot: int) -> None:
        self.__selected_slot = slot

    def get_selected_item(self) -> Item:
        return self.__items[self.__selected_slot]




class Player(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        # Pygame convention for sprites. Attributes kept public.
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 200, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Inventory
        self.__inventory = Inventory()

        # Movement
        self.__vel_x = 0
        self.__vel_y = 0
        self.__speed = 5
        self.__gravity = 0.4
        self.__jump_strength = -12
        self.__on_ground = False


    # Getters and setters
    def get_inventory(self) -> Inventory:
        return self.__inventory

    def update_inventory(self, item: Item) -> None:
        self.__inventory.add_item(item)


    def update(self, tiles: list) -> None:
        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.__vel_x = 0
        if keys[pygame.K_a]:
            self.__vel_x = -self.__speed
        if keys[pygame.K_d]:
            self.__vel_x = self.__speed

        #Vertical movement
        if keys[pygame.K_SPACE] and self.__on_ground:
            self.__vel_y = self.__jump_strength
        self.__vel_y += self.__gravity
        self.__on_ground = False

        # Apply horizontal movement
        self.rect.x += self.__vel_x 

        # Horizontal collisions
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.__vel_x > 0:
                    self.rect.right = tile.rect.left
                elif self.__vel_x < 0:
                    self.rect.left = tile.rect.right  

        # Apply vertical movement
        self.rect.y += self.__vel_y
        
        # Vertical collisions
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.__vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.__vel_y = 0
                    self.__on_ground = True
                elif self.__vel_y < 0:
                    self.rect.top = tile.rect.bottom
                    self.__vel_y = 0


