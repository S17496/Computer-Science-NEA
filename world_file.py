import pygame
import config_file as conf
from tile_file import Tile
import math
import random

class PerlinNoise:
    def __init__(self, seed):
        self.__seed = seed

    def lerp(self, a, b, t):
        return a + (b-a) * t

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

class Chunk:
    def __init__(self):
        self.__tiles = [[0 for _ in range(conf.CHUNK_SIZE)] for _ in range(conf.CHUNK_SIZE)]

    # Getters and setters
    def get_chunk(self) -> list:
        return self.__tiles

    def change_tile(self, x: int, y: int, value: int) -> None:
        self.__tiles[x][y] = value

    def get_tile_id(self, x: int, y: int):
        return self.__tiles[x][y]

class World:
    # Constructor
    def __init__(self, noise1d: PerlinNoise) -> None:
        self.__chunks = self.generate_world(self.generate_surface_heights(noise1d, 15, 25))


    def generate_surface_heights(self, noise1d: PerlinNoise, period: int, amplitude: int) -> list:
        heights = []
        for x in range(conf.CHUNK_SIZE * 20):
            heights.append(int((noise1d.noise(x/period) + 1) * amplitude))
        return heights

    def generate_world(self, heights: list) -> dict:
        world_data = {}
        for x_chunk in range(20):
            for y_chunk in range(10):
                chunk = Chunk()
                for x in range(conf.CHUNK_SIZE):
                    for y in range(conf.CHUNK_SIZE):
                        x_coordinate = x + x_chunk * conf.CHUNK_SIZE
                        y_coordinate = y + y_chunk * conf.CHUNK_SIZE
                        if y_coordinate > heights[x_coordinate]:
                            chunk.change_tile(x, y, -1)
                world_data[(x_chunk, y_chunk)] = chunk                
        return world_data

    # Returns the coordinates of the chunk which a pair of coordinates belong to 
    def which_chunk(self, coordinates: tuple) -> tuple:
        return (coordinates[0] // conf.CHUNK_SIZE, coordinates[1] // conf.CHUNK_SIZE)

    # Returns the coordinates relative to the chunk a pair of coordinates are in
    def where_in_chunk(self, coordinates: tuple) -> tuple:
            return (coordinates[0] // conf.CHUNK_SIZE, coordinates[1] // conf.CHUNK_SIZE)

    # Get nearby rects to player for checking collisions
    def get_nearby_rects(self, rect, range_x: int, range_y: int) -> list:
        world_position_x = rect.centerx // conf.TILE_SIZE
        world_position_y = rect.centery // conf.TILE_SIZE
        nearby = []
        for x in range(-range_x, range_x + 1):
            for y in range(-range_y, range_y + 1):
                chunk_coordinates = self.which_chunk((world_position_x + x, world_position_y + y))
                coordinates_in_chunk = self.where_in_chunk((world_position_x + x, world_position_y + y))
                tile_id = self.__chunks[chunk_coordinates].get_tile_id(coordinates_in_chunk[0], coordinates_in_chunk[1])
                if tile_id > -1:
                    nearby.append(pygame.rect.Rect(world_position_x + x, world_position_y + y, conf.TILE_SIZE, conf.TILE_SIZE))
        return nearby

    def get_nearby_chunks(self, rect, range_x: int, range_y: int) -> dict:
        world_position_x = rect.centerx // conf.TILE_SIZE
        world_position_y = rect.centery // conf.TILE_SIZE
        nearby = {}
        for x in range(-range_x, range_x + 1):
            for y in range(-range_y, range_y + 1):
                nearby[(world_position_x + x, world_position_y + y)] = self.__chunks[(world_position_x + x, world_position_y + y)]
        return nearby 


    def break_tile(self, coordinates: tuple) -> None:
        pass

    def render_world(self, player_rect, screen , camera: object):
        chunks = self.get_nearby_chunks(player_rect, conf.RENDER_DISTANCE, conf.RENDER_DISTANCE)
        for chunk in chunks:
            chunk_data = chunks[chunk]

    # Getters and setters
    def get_chunk(self, coordinates: tuple) -> list:
        return self.__chunks[coordinates]

