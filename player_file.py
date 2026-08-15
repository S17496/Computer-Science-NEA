import pygame
import config_file as c

class Player(pygame.sprite.Sprite):
    # Constructor
    def __init__(self,x,y):
        super().__init__()

        # Pygame convention for sprites. Attributes kept public.
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 200, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

        # Inventory
        self.__inventory = {}

        # Movement
        self.__vel_x = 0
        self.__vel_y = 0
        self.__speed = 5
        self.__gravity = 0.4
        self.__jump_strength = -12
        self.__on_ground = False

    # Getters and setters
    def get_inventory(self):
        return self.__inventory

    def update_inventory(self, item):
        if item in self.__inventory:
            self.__inventory[item] += 1
            print(self.__inventory)
        else:
            self.__inventory[item] = 1
            print(self.__inventory)


    def update(self, tiles):
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

class InventoryUI:
    def __init__(self, font):
        self.__font = font
        self.__box_width = 100

    def render(self, screen, inventory):
        # Draw background box
        background_box = pygame.Rect(200, 200, len(inventory) * (self.__box_width + 20), 100)
        pygame.draw.rect(screen, (50, 50, 50), background_box)

        # Draw items
        x = 210
        for item_name, count in inventory.items():
            text = f"{item_name}: {count}"
            text_surface = self.__font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (x, 15))
            x += self.__box_width + 20