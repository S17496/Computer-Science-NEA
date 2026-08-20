import pygame
import config_file as conf
import inventory_file as inv


    
class InventoryUI:
    def __init__(self, font: pygame.font.Font) -> None:
        self.__font = font
        self.__box_width = 100

    def render_hotbar(self, screen, hotbar_items: list, selected_slot: int) -> None:
        # Draw background box
        background_box = pygame.Rect(200, 200, conf.HOTBAR_SIZE * (self.__box_width + 20), 100)
        pygame.draw.rect(screen, (50, 50, 50), background_box)

        # Draw items
        x = 210
        for item in hotbar_items:
            if item != None:
                text_surface = self.__font.render(f"{item.get_name()}: {item.get_quantity()}", True, (255, 255, 255))
                screen.blit(text_surface, (x, 200))
            x += self.__box_width + 20

        # Draw selected slot
        border = pygame.Rect(210 + selected_slot * (self.__box_width + 20), 200, 10, 10)
        pygame.draw.rect(screen, (255, 255, 255), border)



class Player(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        # Pygame convention for sprites. Attributes kept public.
        self.image = pygame.Surface((60, 90))
        self.image.fill((255, 200, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Inventory
        self.__inventory = inv.Inventory()

        # Movement
        self.__vel_x = 0
        self.__vel_y = 0
        self.__speed = 5
        self.__gravity = 0.6
        self.__jump_strength = -14
        self.__on_ground = False


    # Getters and setters
    def get_inventory(self) -> inv.Inventory:
        return self.__inventory

    def update_inventory(self, item: inv.Item) -> None:
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


