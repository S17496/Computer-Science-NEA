import pygame
import inventory
import entities
import items
import config
import crafting


class Player(entities.Entity):
    # Constructor
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)

        # Health
        self.__max_health = 1000000
        self.__health = 1000000
        self.__regeneration = 0
        self.__spawn_point = (x, y)
        self.__fall_damage_multiplier = 0.2

        # Inventory and crafting
        self.__inventory = inventory.Inventory()
        self.__inventory.add_item(items.Pickaxe("100", 1))

        self.__hand = None

        self.__crafting = crafting.Crafting()

        # Movement
        self.__vel_x = 0
        self.__vel_y = 0
        self.__speed = 5
        self.__jump_strength = -14
        self.__on_ground = False


    # Getters and setters
    def get_inventory(self) -> inventory.Inventory:
        return self.__inventory


    def get_top_left_coordinates(self) -> tuple:
        return (self.rect.x // config.TILE_SIZE, self.rect.y // config.TILE_SIZE)


    def get_bottom_right_coordinates(self) -> tuple:
        return ((self.rect.x + config.PLAYER_WIDTH) // config.TILE_SIZE, (self.rect.y + config.PLAYER_HEIGHT) // config.TILE_SIZE)


    def set_hand(self, item: items.Item | None):
        self.__hand = item


    def get_hand(self) -> items.Item | None:
        return self.__hand


    def swap_hand_item(self, slot: int) -> None:
        
        if slot < 0 or slot >= config.INVENTORY_SIZE:
            return

        inventory_items = self.__inventory.get_items()
        slot_item = inventory_items[slot]
        inventory_items[slot] = self.__hand
        self.__hand = slot_item


    def get_health(self) -> int:
        return self.__health


    def get_max_health(self) -> int:
        return self.__max_health
    

    def update(self, tiles: list, item_entities: list, max_x: int, max_y: int) -> None:

        self.__handle_keys()

        self.__handle_gravity()

        self.__horizontal_movement(tiles, max_x)

        self.__vertical_movement(tiles, max_y)


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


    def __handle_keys(self) -> None:
        """Updates player attributes based on key inputs."""

        keys = pygame.key.get_pressed()

        self.__vel_x = 0

        if keys[pygame.K_a]:
            self.__vel_x = -self.__speed

        if keys[pygame.K_d]:
            self.__vel_x = self.__speed

        if keys[pygame.K_SPACE] and self.__on_ground:
            self.__vel_y = self.__jump_strength


    def __handle_gravity(self) -> None:
        """Applies gravity to player until vertical velocity reaches its maximum."""

        self.__vel_y += config.GRAVITY

        if self.__vel_y > 50:
            self.__vel_y = 50


    def __horizontal_movement(self, tiles: list, max_x: int) -> None:
        """Moves player horizontally by number of pixels equal to its horizontal velocity."""

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

            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(max_x, self.rect.right)


    def __vertical_movement(self, tiles: list, max_y: int) -> None:
        """Moves player vertically by number of pixels equal to its vertical velocity."""

        self.__on_ground = False

        for _ in range(abs(int(self.__vel_y))):

            if self.__vel_y > 0:
                self.rect.y += 1

            elif self.__vel_y < 0:
                self.rect.y -= 1

            if self.rect.bottom > max_y:
                self.rect.bottom = max_y
                self.__vel_y = 0
                self.__on_ground = True
                return

            elif self.rect.top < 0:
                self.rect.top = 0
                self.__vel_y = 0
                return

            # Vertical collisions

            for rect in tiles:
                if self.rect.colliderect(rect):

                    if self.__vel_y > 0:

                        if self.__apply_fall_damage():
                            return

                        self.rect.bottom = rect.top
                        self.__vel_y = 0
                        self.__on_ground = True


                    elif self.__vel_y < 0:

                        self.rect.top = rect.bottom
                        self.__vel_y = 0

                    return


    def take_damage(self, damage: int) -> bool:
        """Takes specified amount of damage away from player's health. Sets health to 0 if it goes below 0."""

        self.__health -= damage 

        if self.__health <= 0:
            self.__die()
            self.__health = self.__max_health
            return True

        return False


    def heal(self, health: int) -> None:
        """Adds specified amount of health to player's health. Sets health to max health if it goes above max health."""

        self.__health += health 

        if self.__health > self.__max_health:
            self.__health = self.__max_health


    def use_life_crystal(self) -> bool:
        """Increases player's maximum health by 20. Limit is 400."""

        if self.__max_health < 400:
            self.__max_health += 20
            return True

        return False


    def __apply_fall_damage(self) -> bool:
        """Player takes damage due to falling if they travel faster than minimum fall damage velocity."""

        if self.__vel_y < config.MIN_FALL_DAMAGE_VEL:
            return False

        damage = round(self.__fall_damage_multiplier * (self.__vel_y - config.MIN_FALL_DAMAGE_VEL) ** 2)

        return self.take_damage(damage)


    def __die(self) -> None:
        """Sets player's location to spawnpoint."""

        self.rect.topleft = self.__spawn_point

        self.__vel_x = 0
        self.__vel_y = 0
        self.__on_ground = False

