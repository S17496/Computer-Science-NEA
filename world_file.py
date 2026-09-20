import pygame
import config_file as conf
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
        rng = random.Random(self.__seed + x)
        return rng.choice([-1, 1])
    
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
        x_cell = self.get_cell_info(x)
        y_cell = self.get_cell_info(y)

        x0 = x_cell[0]
        x1 = x0 + 1

        y0 = y_cell[0]
        y1 = y0 + 1

        dx = x_cell[1]
        dy = y_cell[1]

        gradients = []

        for x in (x0, x1):
            for y in (y0, y1):

                # Hashing algorithm to avoid collisions
                value = self.__seed ^ (x * 614807543)
                value ^= y * 931469120
                value = (value ^ (value >> 13)) * 961379052

                gradient = ((1, 0),(-1, 0),(0, 1),(0, -1),(math.sqrt(2) / 2, math.sqrt(2) / 2),(-math.sqrt(2) / 2, math.sqrt(2) / 2),(math.sqrt(2) / 2, -math.sqrt(2) / 2),(-math.sqrt(2) / 2, -math.sqrt(2) / 2))[value % 8]
                gradients.append(gradient)

        bottom_left_distance = (dx, dy)
        bottom_right_distance = (dx - 1, dy)
        top_left_distance = (dx, dy - 1)
        top_right_distance = (dx - 1, dy - 1)

        bottom_left_influence = bottom_left_distance[0] * gradients[0][0] + bottom_left_distance[1] * gradients[0][1]
        bottom_right_influence = bottom_right_distance[0] * gradients[2][0] + bottom_right_distance[1] * gradients[2][1]
        top_left_influence = top_left_distance[0] * gradients[1][0] + top_left_distance[1] * gradients[1][1]
        top_right_influence = top_right_distance[0] * gradients[3][0] + top_right_distance[1] * gradients[3][1]

        fade_x = self.fade(dx)
        fade_y = self.fade(dy)

        bottom = self.lerp(bottom_left_influence, bottom_right_influence, fade_x)
        top = self.lerp(top_left_influence, top_right_influence, fade_x)

        return self.lerp(bottom, top, fade_y)

class Worm:
    def __init__(self, seed, x, y) -> None:
        self.__x = x 
        self.__y = y 
        self.__rng = random.Random(seed)
        self.__angle = self.__rng.uniform(0, math.pi)

    def step(self) -> None:
        self.__angle += self.__rng.uniform(-0.3, 0.3)
        self.__x += math.cos(self.__angle)
        self.__y += math.sin(self.__angle)

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    
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
    def __init__(self, seed) -> None:
        self.__seed = seed
        self.__perlin_noise = PerlinNoise(seed)
        self.__surface_heights = self.generate_surface_heights(self.__perlin_noise, 25, 25, 4)

        with open("tile_data.json", "r") as tile_data:
            self.__tile_data = json.load(tile_data)

        # Converts file paths in tile data to pygame images
        for tile_id in self.__tile_data:
            texture_path = self.__tile_data[tile_id]["texture"]
            self.__tile_data[tile_id]["texture"] = pygame.image.load(texture_path).convert_alpha()

        self.__chunks = self.generate_world(self.__surface_heights)
        self.generate_caves()


    def generate_surface_heights(self, noise: PerlinNoise, period: int, amplitude: int, layers: int) -> list:
        heights = []

        base_height = conf.WORLD_HEIGHT * conf.CHUNK_SIZE // 2

        for x in range(conf.CHUNK_SIZE * conf.WORLD_WIDTH):
            height = 0
            octave_amplitude = 1
            frequency = 1
            maximum_amplitude = 0

            for _ in range(layers):
                height += noise.noise1D(x / period * frequency) * octave_amplitude
                maximum_amplitude += octave_amplitude
                octave_amplitude *= 0.5
                frequency *= 2

            height /= maximum_amplitude
            height = base_height + int(height * amplitude)
            heights.append(height)

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
    
    def carve_circle(self, center_x, center_y, radius):
        for x in range(center_x - radius, center_x + radius + 1):
            for y in range(center_y - radius, center_y + radius + 1):

                if (x - center_x) ** 2 + (y - center_y) ** 2 > radius ** 2:
                    continue

                chunk_coords = self.which_chunk((x, y))

                if chunk_coords not in self.__chunks:
                    continue

                chunk = self.__chunks[chunk_coords]

                coords_in_chunk = self.where_in_chunk((x, y))

                chunk.change_tile(coords_in_chunk, -1)

    def generate_caves(self) -> None:
        rng = random.Random(self.__seed)
        start_x = rng.randrange(conf.CHUNK_SIZE * conf.WORLD_WIDTH)
        start_y = rng.randrange(self.__surface_heights[start_x], conf.CHUNK_SIZE * conf.WORLD_HEIGHT // 2 + self.__surface_heights[start_x])
        
        for worm_number in range(10):
            worm = Worm(self.__seed + worm_number, start_x, start_y)
            for _ in range(rng.randrange(500, 1000)):
                self.carve_circle(int(worm.get_x()) , int(worm.get_y()), rng.randrange(5, 8))
                worm.step()


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
        chunk_coordinates = self.which_chunk(coordinates)
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