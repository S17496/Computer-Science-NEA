import pygame
import config_file as conf
import math
import random
import json


class PerlinNoise:
    def __init__(self, seed):
        self.__seed = seed
        self.__gradient_cache = {}

    def lerp(self, a, b, t):
        return a + (b-a) * t

    def get_cell_info(self, x):
        return (math.floor(x), x - math.floor(x))

    def fade(self, x):
        return 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3

    def get_gradient(self, x):
        rng = random.Random(self.__seed + x)
        return rng.choice([-1, 1])

    def get_gradient_2d(self, x, y):
        key = (x, y)

        if key not in self.__gradient_cache:
            value = self.__seed ^ (x * 614807543)
            value ^= y * 931469120
            value = (value ^ (value >> 13)) * 961379052
            self.__gradient_cache[key] = conf.GRADIENTS_2D[value % 8]

        return self.__gradient_cache[key]
    
    def noise1D(self, x):
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

    def noise2D(self, x, y):
        x0 = math.floor(x)
        x1 = x0 + 1
        y0 = math.floor(y)
        y1 = y0 + 1

        dx = x - x0
        dy = y - y0

        # Get gradient at each corner
        bottom_left_gradient = self.get_gradient_2d(x0, y1)
        top_left_gradient = self.get_gradient_2d(x0, y0)
        bottom_right_gradient = self.get_gradient_2d(x1, y1)
        top_right_gradient = self.get_gradient_2d(x1, y0)

        bottom_left_distance = (dx, dy)
        bottom_right_distance = (dx - 1, dy)
        top_left_distance = (dx, dy - 1)
        top_right_distance = (dx - 1, dy - 1)

        bottom_left_influence = bottom_left_distance[0] * bottom_left_gradient[0] + bottom_left_distance[1] * bottom_left_gradient[1]
        bottom_right_influence = bottom_right_distance[0] * bottom_right_gradient[0] + bottom_right_distance[1] * bottom_right_gradient[1]
        top_left_influence = top_left_distance[0] * top_left_gradient[0] + top_left_distance[1] * top_left_gradient[1]
        top_right_influence = top_right_distance[0] * top_right_gradient[0] + top_right_distance[1] * top_right_gradient[1]

        fade_x = self.fade(dx)
        fade_y = self.fade(dy)

        bottom = self.lerp(bottom_left_influence, bottom_right_influence, fade_x)
        top = self.lerp(top_left_influence, top_right_influence, fade_x)

        return self.lerp(bottom, top, fade_y)


    
class Chunk:
    def __init__(self, coordinates: tuple) -> None:
        self.__tiles = [[-1 for _ in range(conf.CHUNK_SIZE)] for _ in range(conf.CHUNK_SIZE)]

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
    def __init__(self, seed) -> None:
        self.__seed = seed
        self.__perlin_noise = PerlinNoise(seed)

        with open("tile_data.json", "r") as tile_data:
            self.__tile_data = json.load(tile_data)

        # Converts file paths in tile data to pygame images
        for tile_id in self.__tile_data:
            texture_path = self.__tile_data[tile_id]["texture"]
            self.__tile_data[tile_id]["texture"] = pygame.image.load(texture_path).convert_alpha()

        self.__chunks = {}
        self.__surface_heights = {}
        self.__stone_heights = {}


    def get_or_create_chunk(self, chunk_coordinates) -> Chunk:

        if chunk_coordinates not in self.__chunks:
            self.__chunks[chunk_coordinates] = self.generate_chunk(chunk_coordinates)

        return self.__chunks[chunk_coordinates]


    def generate_chunk(self, chunk_coordinates) -> Chunk:

        chunk_x, chunk_y = chunk_coordinates
        chunk = Chunk(chunk_coordinates)

        for x in range(conf.CHUNK_SIZE):
            world_x = chunk_x * conf.CHUNK_SIZE + x 

            surface_height = self.get_surface_height(world_x)
            stone_height = self.get_stone_height(world_x)

            for y in range(conf.CHUNK_SIZE):
                world_y = chunk_y * conf.CHUNK_SIZE + y

                if world_y < surface_height:
                    tile_id = -1
                elif world_y < stone_height:
                    tile_id = 0
                else:
                    tile_id = 1

                chunk.change_tile((x, y), tile_id)

        self.generate_caves_for_chunk(chunk, chunk_coordinates, 100, 0.05)
        return chunk


    def unload_far_chunks(self, player_rect):
        player_x = player_rect.centerx // conf.TILE_SIZE
        player_y = player_rect.centery // conf.TILE_SIZE
        current_chunk = self.which_chunk((player_x, player_y))

        max_distance = conf.RENDER_DISTANCE + 2

        for chunk_coordinates in list(self.__chunks):
            distance_x = abs(chunk_coordinates[0] - current_chunk[0])
            distance_y = abs(chunk_coordinates[1] - current_chunk[1])

            if distance_x > max_distance or distance_y > max_distance:
                del self.__chunks[chunk_coordinates]


    def generate_height(self, x: int, base_height: int, period: int, amplitude: int, layers: int) -> int:
        
        height = 0
        octave_amplitude = 1
        frequency = 1
        maximum_amplitude = 0

        for _ in range(layers):
            height += self.__perlin_noise.noise1D(x / period * frequency) * octave_amplitude
            maximum_amplitude += octave_amplitude
            octave_amplitude *= 0.5
            frequency *= 2

        height /= maximum_amplitude
        height = base_height + int(height * amplitude)

        return height


    def get_surface_height(self, x: int) -> int:
        if x not in self.__surface_heights:
            self.__surface_heights[x] = self.generate_height(x, conf.WORLD_HEIGHT * conf.CHUNK_SIZE // 2, 25, 25, 4)
        return self.__surface_heights[x]


    def get_stone_height(self, x: int) -> int:
        if x not in self.__stone_heights:
            self.__stone_heights[x] = self.generate_height(x, conf.WORLD_HEIGHT * conf.CHUNK_SIZE // 2 + 25, 40, 12, 3)
        return self.__stone_heights[x]



    def generate_caves_for_chunk(self, chunk: Chunk, chunk_coordinates: tuple, period: int, threshold: float) -> None:

        for x in range(conf.CHUNK_SIZE):
            for y in range(conf.CHUNK_SIZE):
                world_x = chunk_coordinates[0] * conf.CHUNK_SIZE + x 
                world_y = chunk_coordinates[1] * conf.CHUNK_SIZE + y 

                if world_y >= self.__surface_heights[world_x]:
                    noise_value = self.__perlin_noise.noise2D(world_x / period, world_y / period)

                    if abs(noise_value) <= threshold:
                        chunk.change_tile((x, y), -1)



    def generate_ore(self, ore: int, ore_threshold) -> None:
        
        for chunk_coordinates in self.__chunks:
            chunk = self.__chunks[chunk_coordinates]

            for x in range(conf.CHUNK_SIZE):
                for y in range(conf.CHUNK_SIZE):
                    world_x = chunk_coordinates[0] * conf.CHUNK_SIZE + x 
                    world_y = chunk_coordinates[1] * conf.CHUNK_SIZE + y 

                    noise_value = self.__perlin_noise.noise2D(world_x/10, world_y/10)
                    if abs(noise_value) <= ore_threshold and chunk.get_tile_id((x, y)) == 1:
                        chunk.change_tile((x, y), ore)



    def generate_ore_data(self) -> list:

        ores_data = []

        for tile_id in self.__tile_data:

            ore_data = self.__tile_data[tile_id]
            if "ore_threshold" in ore_data:
                ores_data.append((int(tile_id), ore_data["ore_threshold"]))

        return ores_data


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

                chunk = self.get_or_create_chunk(chunk_coordinates)
                tile_rect = chunk.get_tile_rect(coordinates_in_chunk)
                
                if tile_rect is not None:
                    nearby.append(tile_rect)
        return nearby

    def get_nearby_chunks(self, rect, range_x: int, range_y: int) -> dict:
        world_position_x = rect.centerx // conf.TILE_SIZE
        world_position_y = rect.centery // conf.TILE_SIZE

        current_chunk_coordinates = self.which_chunk((world_position_x, world_position_y))

        nearby = {}

        for x in range(-range_x, range_x + 1):
            for y in range(-range_y, range_y + 1):
                chunk_coordinates = (current_chunk_coordinates[0] + x, current_chunk_coordinates[1] + y)
                # MIGHT NEED CHANGING FOR WHEN PLAYER IS AT EDGE OF WORLD
                nearby[chunk_coordinates] = self.get_or_create_chunk(chunk_coordinates)
        return nearby 


    def break_tile(self, coordinates: tuple) -> None:
        chunk_coordinates = self.which_chunk(coordinates)
        coordinates_in_chunk = self.where_in_chunk(coordinates)
        self.__chunks[chunk_coordinates].change_tile(coordinates_in_chunk, -1)


    def render_world(self, player_rect, screen, camera) -> None:
        chunks = self.get_nearby_chunks(player_rect, conf.RENDER_DISTANCE, conf.RENDER_DISTANCE)

        for chunk in chunks.values():
            chunk.render(screen, camera, self.__tile_data)


    # Getters and setters
    def get_chunk(self, coordinates: tuple) -> list:
        return self.__chunks[coordinates]

    def get_item_id(self, tile_id: str) -> str:
        return self.__tile_data[tile_id]["item_id"]

    def get_chunks(self) -> dict:
        return self.__chunks