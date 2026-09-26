import pygame
import inventory_file as inv
import entity_file as ent
import items_file as items
import config_file as conf


class Player(ent.Entity):
    # Constructor
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)

        # Inventory
        self.__inventory = inv.Inventory()

        # Movement
        self.__vel_x = 0
        self.__vel_y = 0
        self.__speed = 5
        self.__gravity = conf.GRAVITY
        self.__jump_strength = -14
        self.__on_ground = False


    # Getters and setters
    def get_inventory(self) -> inv.Inventory:
        return self.__inventory

    def update_inventory(self, item: items.Item) -> None:
        self.__inventory.add_item(item)

    def get_top_left_coordinates(self) -> tuple:
        return (self.rect.x // conf.TILE_SIZE, self.rect.y // conf.TILE_SIZE)

    def get_bottom_right_coordinates(self) -> tuple:
        return ((self.rect.x + conf.PLAYER_WIDTH) // conf.TILE_SIZE, (self.rect.y + conf.PLAYER_HEIGHT) // conf.TILE_SIZE)


    def update(self, tiles: list, item_entities: list) -> None:
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
        for _ in range(abs(int(self.__vel_x))):
            if self.__vel_x > 0:
                self.rect.x += 1
            elif self.__vel_x < 0:
                self.rect.x -= 1
            # Horizontal collisions
            for rect in tiles:
                if self.rect.colliderect(rect):
                    if self.__vel_x > 0:
                        self.rect.right = rect.left
                    elif self.__vel_x < 0:
                        self.rect.left = rect.right

        # Apply vertical movement
        for _ in range(abs(int(self.__vel_y))):
            if self.__vel_y > 0:
                self.rect.y += 1
            elif self.__vel_y < 0:
                self.rect.y -= 1
            # Vertical collisions
            for rect in tiles:
                if self.rect.colliderect(rect):
                    if self.__vel_y > 0:
                        self.rect.bottom = rect.top
                        self.__vel_y = 0
                        self.__on_ground = True
                    elif self.__vel_y < 0:
                        self.rect.top = rect.bottom
                        self.__vel_y = 0

        # Item pickup
        for dropped_item in item_entities:
            if self.rect.colliderect(dropped_item.rect):
                item = dropped_item.get_item()
                self.__inventory.add_item(item)

        # Remove items with no count
        items = self.__inventory.get_items()
        for i in range(len(items)):

            if items[i] is None:
                continue 

            if items[i].get_quantity() == 0:
                self.__inventory.remove_item(i)




