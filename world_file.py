import pygame
import config_file as conf
import tile_file as t
import math
import random

class PerlinNoise:
    def __init__(self, seed):
        self.__seed = seed

    def lerp(self, a, b, t):
        return a + (b-a)*t

    def get_cell_info(self, x):
        return (math.floor(x), x - math.floor(x))

    def fade(self, x):
        return 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3

    def get_gradient(self, x):
        random.seed(self.__seed + x)
        return random.choice([1, -1])
    
    def noise(self, x):
        cell_info = self.get_cell_info(x)

        left = cell_info[0]
        right = left + 1

        distance_left = cell_info[1]
        distance_right = distance_left - 1

        left_gradient = self.get_gradient(left)
        right_gradient = self.get_gradient(right)

        left_influence = left_gradient * distance_left
        right_influence = right_gradient * distance_right

        fade = self.fade(distance_left)

        return self.lerp(left_influence, right_influence, fade)




class World:
    # Constructor
    def __init__(self, noise1d):
        self._tile_group = pygame.sprite.Group()
        self._tile_dic = {}
        self.__world_data = self.generate_world(noise1d)
        self.load(self.__world_data)

    def generate_world(self, noise1d):
        world_data = []
        for y in range(20):
            world_data.append([])
            for x in range(1000):
                world_data[y].append(0)
        for x in range(1000):
            height = int(noise1d.noise(x/10)*5+3)
            for y in range(height, 20):
                world_data[y][x] = 1
        return world_data


    # Load world
    def load(self, world_data):
        # Create a sprite group and dictionary for tiles
        for row_index, row in enumerate(world_data):
            for col_index, tile_id in enumerate(row):
                    if tile_id != 0:
                        new_tile = t.Tile(col_index * conf.TILE_SIZE, row_index * conf.TILE_SIZE, tile_id)
                        self._tile_group.add(new_tile)
                        self._tile_dic[(col_index, row_index)] = new_tile

    # Get nearby tiles to player
    def get_nearby(self, rect):
        position_x = rect.centerx // conf.TILE_SIZE
        position_y = rect.centery // conf.TILE_SIZE
        nearby = []
        for i in range(position_x - 2, position_x + 3):
            for j in range(position_y - 2, position_y + 3):
                if (i,j) in self._tile_dic:
                    nearby.append(self._tile_dic[(i,j)])
        return nearby

    def break_tile(self, coordinates):
        if coordinates in self._tile_dic:
            broken_tile = self._tile_dic.pop(coordinates)
            self._tile_group.remove(broken_tile)

