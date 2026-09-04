import pygame
import config_file as conf
from tile_file import Tile
import math
import random
import json

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
    def __init__(self, coordinates: tuple) -> None:
        self.__tiles = [[0 for _ in range(conf.CHUNK_SIZE)] for _ in range(conf.CHUNK_SIZE)]

        self.__coordinates = coordinates

        self.__dirty = True

        chunk_pixel_size = conf.CHUNK_SIZE * conf.TILE_SIZE
        self.__surface = pygame.Surface((chunk_pixel_size, chunk_pixel_size), pygame.SRCALPHA).convert_alpha()


    def rebuild_surface(self, tile_data: dict) -> None:
        # Surface set to invisible
        self.__surface.fill((0, 0, 0, 0))

        for x in range(conf.CHUNK_SIZE):
            for y in range(conf.CHUNK_SIZE):

                tile_id = self.__tiles[x][y]

                # Keep air invisible
                if tile_id == -1:
                    continue

                texture = tile_data[str(tile_id)]["texture"]
   
                self.__surface.blit(texture, (x * conf.TILE_SIZE, y * conf.TILE_SIZE))

        self.__dirty = False

    def render(self, screen, camera: object, tile_data: dict) -> None:
        if self.__dirty:
            self.rebuild_surface(tile_data)

        chunk_world_x = (self.__coordinates[0] * conf.CHUNK_SIZE * conf.TILE_SIZE)
        chunk_world_y = (self.__coordinates[1] * conf.CHUNK_SIZE * conf.TILE_SIZE)

        screen.blit(self.__surface, (chunk_world_x - camera.get_x(), chunk_world_y - camera.get_y()))


    # Getters and setters

    def get_tile_rect(self, coordinates_in_chunk: tuple) -> pygame.rect.Rect:
        """Returns a rect object with correct world coordinates based on its tile coordinates in the chunk."""
        if self.__tiles[coordinates_in_chunk[0]][coordinates_in_chunk[1]] >= 0:
            left = (self.__coordinates[0] * conf.CHUNK_SIZE + coordinates_in_chunk[0]) * conf.TILE_SIZE
            top = (self.__coordinates[1] * conf.CHUNK_SIZE + coordinates_in_chunk[1]) * conf.TILE_SIZE
            return pygame.rect.Rect(left, top, conf.TILE_SIZE, conf.TILE_SIZE)

    def change_tile(self, coordinates_in_chunk, value: int) -> None:
        self.__tiles[coordinates_in_chunk[0]][coordinates_in_chunk[1]] = value
        self.__dirty = True

    def get_tile_id(self, coordinates_in_chunk: tuple) -> int:
        return self.__tiles[coordinates_in_chunk[0]][coordinates_in_chunk[1]]

class World:
    # Constructor
    def __init__(self, noise1d: PerlinNoise) -> None:
        with open("tile_data.json", "r") as tile_data:
            self.__tile_data = json.load(tile_data)

        # Converts file paths in tile data to pygame images
        for tile_id in self.__tile_data:
            texture_path = self.__tile_data[tile_id]["texture"]
            self.__tile_data[tile_id]["texture"] = pygame.image.load(texture_path).convert_alpha()

        self.__chunks = self.generate_world(self.generate_surface_heights(noise1d, 15, 25))


    def generate_surface_heights(self, noise1d: PerlinNoise, period: int, amplitude: int) -> list:
        heights = []
        for x in range(conf.CHUNK_SIZE * conf.WORLD_WIDTH):
            heights.append(int((noise1d.noise(x/period) + 1) * amplitude))
        return heights

    def generate_world(self, heights: list) -> dict:
        world_data = {}
        for x_chunk in range(conf.WORLD_WIDTH):
            for y_chunk in range(conf.WORLD_HEIGHT):
                chunk = Chunk((x_chunk, y_chunk))
                for x in range(conf.CHUNK_SIZE):
                    for y in range(conf.CHUNK_SIZE):
                        x_coordinate = x + x_chunk * conf.CHUNK_SIZE
                        y_coordinate = y + y_chunk * conf.CHUNK_SIZE
                        if y_coordinate < heights[x_coordinate]:
                            chunk.change_tile((x, y), -1)
                chunk.rebuild_surface(self.__tile_data)
                world_data[(x_chunk, y_chunk)] = chunk                
        return world_data


    def which_chunk(self, tile_coordinates: tuple) -> tuple:
        """Returns chunk coordinates based on tile coordinates."""
        return (tile_coordinates[0] // conf.CHUNK_SIZE, tile_coordinates[1] // conf.CHUNK_SIZE)


    def where_in_chunk(self, coordinates: tuple) -> tuple:
        """Returns tile coordinates in chunk based on tile coordinates."""
        return (coordinates[0] % conf.CHUNK_SIZE, coordinates[1] % conf.CHUNK_SIZE)

    # Get nearby rects to player for checking collisions
    def get_nearby_rects(self, rect, range_x: int, range_y: int) -> list:
        """Returns a list of tile rects around a rect."""
        world_position_x = rect.centerx // conf.TILE_SIZE
        world_position_y = rect.centery // conf.TILE_SIZE
        nearby = []
        for x in range(-range_x, range_x + 1):
            for y in range(-range_y, range_y + 1):
                chunk_coordinates = self.which_chunk((world_position_x + x, world_position_y + y))
                coordinates_in_chunk = self.where_in_chunk((world_position_x + x, world_position_y + y))
                if chunk_coordinates in self.__chunks:
                    chunk = self.__chunks[(chunk_coordinates)]
                    tile_rect = chunk.get_tile_rect(coordinates_in_chunk)
                    if tile_rect != None:
                        nearby.append(tile_rect)
        return nearby

    def get_nearby_chunks(self, rect, range_x: int, range_y: int) -> dict:
        world_position_x = rect.centerx // conf.TILE_SIZE
        world_position_y = rect.centery // conf.TILE_SIZE

        current_chunk = self.which_chunk((world_position_x, world_position_y))

        nearby = {}

        for x in range(-range_x, range_x + 1):
            for y in range(-range_y, range_y + 1):
                chunk_coordinates = (current_chunk[0] + x, current_chunk[1] + y)
                if chunk_coordinates in self.__chunks:
                    nearby[chunk_coordinates] = self.__chunks[chunk_coordinates]
        return nearby 


    def break_tile(self, coordinates: tuple) -> None:
        chunk_coordinates = self.get_chunk(coordinates)
        coordinates_in_chunk = self.where_in_chunk(coordinates)
        self.__chunks[chunk_coordinates].change_tile(coordinates_in_chunk, -1)


    def render_world(self, player_rect, screen, camera: object) -> None:
        chunks = self.get_nearby_chunks(player_rect, conf.RENDER_DISTANCE, conf.RENDER_DISTANCE)

        for chunk in chunks.values():
            chunk.render(screen, camera, self.__tile_data)


    # Getters and setters
    def get_chunk(self, coordinates: tuple) -> list:
        return self.__chunks[coordinates]

    def get_item_id(self, tile_id: str) -> str:
        return self.__tile_data[tile_id]["drops"]["item_id"]

    def get_chunks(self) -> dict:
        return self.__chunks