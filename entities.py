import pygame
import random 
import config


class Entity(pygame.sprite.Sprite):
    # Constructor
        def __init__(self, x: int, y: int, image: str) -> None:
            super().__init__()

            # Pygame convention for sprites. Attributes kept public.
            self.image = pygame.image.load(image)
            self.rect = self.image.get_rect(topleft=(x, y))

        def update(self) -> None:
            return


class StaticEntity(Entity):
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)

        self.__health = 0
        self.__drops = {}
        self.__dimensions = ()


    def take_damage(self, damage: int) -> None:

        self.__health -= damage 

        if self.__health < 0:
            self.__health = 0


    def get_dimensions(self) -> tuple:
        return self.__dimensions


    def update(self, screen, camera) -> None:
        screen.blit(self.image, (self.rect.x - camera.get_x(), self.rect.y - camera.get_y()))


    def __destroy(self) -> dict:
        return self.__drops


class Tree(StaticEntity):
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)

        self.__health = 100
        self.__drops = {"5": random.randint(5, 20)}
        self.__dimensions = (2,10)


class Sapling(StaticEntity):

    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)

        self.__health = 1
        self.__drops = {}
        self.__age = 0


    def request_to_grow(self) -> bool:

        if self.__age < config.TREE_GROW_TIME:
            self.__age += 1

        if self.__age == config.TREE_GROW_TIME:
            return True

        return False


    


class ItemEntity(Entity):
    # Constructor
    def __init__(self, x: int, y: int, image: str, item) -> None:
        super().__init__(x, y, image)
        self.__item = item
        self.__vel_y = 0
        self.__gravity = config.GRAVITY

    def get_item(self) -> object:
        return self.__item

    def update(self, tiles, item_entities):

        # Apply vertical movement
        self.rect.y += self.__vel_y
        self.__vel_y += self.__gravity 

        # Collisions
        for rect in tiles:
            if self.rect.colliderect(rect):
                if self.__vel_y > 0:
                    self.rect.bottom = rect.top
                    self.__vel_y = 0
                elif self.__vel_y < 0:
                    self.rect.top = rect.bottom
                    self.__vel_y = 0


        for item_entity in item_entities:

            if item_entity is self:
                continue

            item = item_entity.get_item()
            total = self.__item.get_quantity() + item.get_quantity()

            if item.get_name() == self.__item.get_name() and total <= self.__item.get_max_stack():
                item.set_quantity(total)
                self.__item.set_quantity(0)

        # Delete dropped items with no item
        if self.__item.get_quantity() == 0:
            self.kill()



class Enemy(Entity):

    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)


    def update(self) -> None:
        return self.__movement_ai()


    def __movement_ai(self) -> None:
        """Enemy decides where to move.."""
        return


class Zombie(Enemy):
    def __init__(self, x: int, y: int, image: str) -> None:
        super().__init__(x, y, image)
        self.__speed = 1
        self.__jump_strength = -14
        self.__on_ground = False
        self.__vel_y = 0
        self.__aggro_distance = config.TILE_SIZE * 20


    def update(self, player_rect: pygame.Rect, tiles: list) -> None:

        self.__movement_ai(player_rect, tiles)
        self.__vertical_motion(tiles)


    def __movement_ai(self, player_rect: pygame.Rect, tiles: list) -> None:
        """Enemy decides where to move."""

        player_distance = player_rect.x - self.rect.x

        if player_distance > self.__aggro_distance:
            return

        if player_distance > 0:
            return self.__move_right(tiles)

        if player_distance < 0:
            return self.__move_left(tiles)


    def __move_right(self, tiles) -> None:
        """Zombie moves right and jumps if collision occurs"""

        for _ in range(int(self.__speed)):

            self.rect.x += 1

            for rect in tiles:
                if self.rect.colliderect(rect):

                    self.rect.right = rect.left

                    self.__vel_y = self.__jump_strength
                    self.__on_ground = False


    def __move_left(self, tiles) -> None:
        """Zombie moves left and jumps if collision occurs."""

        for _ in range(int(self.__speed)):

            self.rect.x -= 1

            for rect in tiles:
                if self.rect.colliderect(rect):

                    self.rect.left = rect.right

                    if self.__on_ground:
                        self.__vel_y = self.__jump_strength
                        self.__on_ground = False


    def __vertical_motion(self, tiles) -> None:
        """Zombie moves vertically and accelerates due to gravity."""

        for _ in range(abs(int(self.__vel_y))):

            if self.__vel_y > 0:
                self.rect.y += 1

            if self.__vel_y < 0:
                self.rect.y -= 1

            for rect in tiles:

                if self.rect.colliderect(rect):

                    if self.__vel_y > 0:
                        self.rect.bottom = rect.top
                        self.__on_ground = True
                        self.__vel_y = 0

                    elif self.__vel_y < 0:
                        self.rect.top = rect.bottom

        self.__vel_y += config.GRAVITY
            