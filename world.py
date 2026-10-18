import pygame
import config
import math
import random
import json
import os 


class PerlinNoise:
    def __init__(self, seed):
        self.__seed = seed
        self.__gradient_2d_cache = {}
        self.__gradient_1d_cache = {}


    def lerp(self, a, b, t):
        return a + (b-a) * t


    def fade(self, x):
        return 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3


    def get_gradient_1d(self, x):
        
        if x not in self.__gradient_1d_cache:
            rng = random.Random(self.__seed + x)
            self.__gradient_1d_cache[x] = rng.choice([-1, 1])

        return self.__gradient_1d_cache[x]


    def get_gradient_2d(self, x, y):
        key = (x, y)

        if key not in self.__gradient_2d_cache:
            value = self.__seed ^ (x * 614807543)
            value ^= y * 931469120
            value = (value ^ (value >> 13)) * 961379053
            self.__gradient_2d_cache[key] = config.GRADIENTS_2D[value % 8]

        return self.__gradient_2d_cache[key]

    
    def noise1D(self, x):

        x0 = math.floor(x)
        x1 = x0 + 1
        dx = x - x0

        g0 = self.get_gradient_1d(x0)
        g1 = self.get_gradient_1d(x1)

        n0 = g0 * dx
        n1 = g1 * (dx-1)

        fade = self.fade(dx)

        return self.lerp(n0, n1, fade)


    def noise2D(self, x, y):
        x0 = math.floor(x)
        x1 = x0 + 1
        y0 = math.floor(y)
        y1 = y0 + 1

        dx = x - x0
        dy = y - y0

        # Get gradient at each corner
        g00 = self.get_gradient_2d(x0, y0)
        g01 = self.get_gradient_2d(x0, y1)
        g10 = self.get_gradient_2d(x1, y0)
        g11 = self.get_gradient_2d(x1, y1)

        # Dot product to calculate gradient influence
        n00 = dx * g00[0] + dy * g00[1]
        n01 = dx * g01[0] + (dy-1) * g01[1]
        n10 = (dx-1) * g10[0] + dy * g10[1]
        n11 = (dx-1) * g11[0] + (dy-1) * g11[1]

        fade_x = self.fade(dx)
        fade_y = self.fade(dy)

        top = self.lerp(n00, n10, fade_x)
        bottom = self.lerp(n01, n11, fade_x)

        return self.lerp(top, bottom, fade_y)


class Chunk:
    def __init__(self, coordinates: tuple, tiles: list | None = None, modified: bool = False) -> None:

        if tiles is None:
            tiles = [[-1 for _ in range(config.CHUNK_SIZE)]for _ in range(config.CHUNK_SIZE)]

        self.__tiles = tiles

        self.__coordinates = coordinates

        self.__dirty = True

        self.__modified = modified

        chunk_pixel_size = config.CHUNK_SIZE * config.TILE_SIZE
        self.__surface = pygame.Surface((chunk_pixel_size, chunk_pixel_size), pygame.SRCALPHA).convert_alpha()


    def rebuild_surface(self, tile_data: dict) -> None:
        # Surface set to invisible
        self.__surface.fill((0, 0, 0, 0))

        for x in range(config.CHUNK_SIZE):
            for y in range(config.CHUNK_SIZE):

                tile_id = self.__tiles[x][y]

                # Keep air invisible
                if tile_id == -1:
                    continue

                texture = tile_data[str(tile_id)]["texture"]
   
                self.__surface.blit(texture, (x * config.TILE_SIZE, y * config.TILE_SIZE))

        self.__dirty = False


    def render(self, screen, camera: object, tile_data: dict) -> None:
        if self.__dirty:
            self.rebuild_surface(tile_data)

        chunk_world_x = (self.__coordinates[0] * config.CHUNK_SIZE * config.TILE_SIZE)
        chunk_world_y = (self.__coordinates[1] * config.CHUNK_SIZE * config.TILE_SIZE)

        screen.blit(self.__surface, (chunk_world_x - camera.get_x(), chunk_world_y - camera.get_y()))


    def get_tile_rect(self, coordinates_in_chunk: tuple) -> pygame.rect.Rect:
        """Returns a rect object with correct world coordinates based on its tile coordinates in the chunk."""

        if self.__tiles[coordinates_in_chunk[0]][coordinates_in_chunk[1]] >= 0:
            left = (self.__coordinates[0] * config.CHUNK_SIZE + coordinates_in_chunk[0]) * config.TILE_SIZE
            top = (self.__coordinates[1] * config.CHUNK_SIZE + coordinates_in_chunk[1]) * config.TILE_SIZE
            return pygame.rect.Rect(left, top, config.TILE_SIZE, config.TILE_SIZE)


    def change_tile(self, coordinates_in_chunk: tuple, value: int, mark_dirty: bool = True) -> None:

        self.__tiles[coordinates_in_chunk[0]][coordinates_in_chunk[1]] = value

        if mark_dirty:
            self.__dirty = True
            self.__modified = True


    def get_tile_id(self, coordinates_in_chunk: tuple) -> int:
        return self.__tiles[coordinates_in_chunk[0]][coordinates_in_chunk[1]]


    def get_modified(self) -> bool:
        return self.__modified


    def mark_dirty(self) -> None:
        self.__dirty = True


    def get_tiles(self) -> list:
        return [row[:] for row in self.__tiles]


class World:
    # CONSTRUCTOR

    def __init__(self, name, seed) -> None:
        self.__name = name
        self.__perlin_noise = PerlinNoise(seed)

        with open("data/tiles.json", "r") as tile_data:
            self.__tile_data = json.load(tile_data)

        # Converts texture file paths in tile data to pygame images
        for tile_id in self.__tile_data:
            texture_path = self.__tile_data[tile_id]["texture"]
            self.__tile_data[tile_id]["texture"] = pygame.image.load(texture_path).convert_alpha()

        self.__surface_heights = {}
        self.__stone_heights = {}
        self.__ore_thresholds = self.__generate_ore_thresholds()

        self.__chunks = self.__load_saved_chunks()
        self.__chunk_queue = []


    # CHUNK GENERATION

    def __generate_chunk(self, chunk_coordinates: tuple) -> Chunk:

        chunk_x, chunk_y = chunk_coordinates
        chunk = Chunk(chunk_coordinates)

        for x in range(config.CHUNK_SIZE):
            world_x = chunk_x * config.CHUNK_SIZE + x 

            surface_height = self.__get_surface_height(world_x)
            stone_height = self.__get_stone_height(world_x)

            for y in range(config.CHUNK_SIZE):
                world_y = chunk_y * config.CHUNK_SIZE + y

                if world_y < surface_height:
                    tile_id = -1
                elif world_y < stone_height:
                    tile_id = 0
                else:
                    tile_id = 1

                chunk.change_tile((x, y), tile_id, False)

        self.__generate_caves(chunk, chunk_coordinates)
        self.__generate_ores(chunk, chunk_coordinates)

        chunk.mark_dirty()

        return chunk


    # CHUNK LIFECYCLE

    def unload_far_chunks(self, player_rect) -> None:
        player_x = player_rect.centerx // config.TILE_SIZE
        player_y = player_rect.centery // config.TILE_SIZE
        current_chunk = self.which_chunk((player_x, player_y))

        for chunk_coordinates in list(self.__chunks):

            if self.__chunks[chunk_coordinates].get_modified():
                continue
            
            distance_x = abs(chunk_coordinates[0] - current_chunk[0])
            distance_y = abs(chunk_coordinates[1] - current_chunk[1])

            if distance_x > config.UNLOAD_DISTANCE or distance_y > config.UNLOAD_DISTANCE:
                del self.__chunks[chunk_coordinates]


    # TERRAIN GENERATION

    def __generate_height(self, x: int, base_height: int, period: int, amplitude: int, layers: int) -> int:
        
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


    def __get_surface_height(self, x: int) -> int:
        if x not in self.__surface_heights:
            self.__surface_heights[x] = self.__generate_height(x, config.WORLD_HEIGHT * config.CHUNK_SIZE // 2, 25, 25, 4)
        return self.__surface_heights[x]


    def __get_stone_height(self, x: int) -> int:
        if x not in self.__stone_heights:
            self.__stone_heights[x] = self.__generate_height(x, config.WORLD_HEIGHT * config.CHUNK_SIZE // 2 + 25, 40, 12, 3)
        return self.__stone_heights[x]


    # CAVES AND ORES

    def __generate_noise_for_chunk(self, chunk_coordinates: tuple, period: int, layers: int, count: int) -> list:

        noise = []

        for x in range(config.CHUNK_SIZE):

            x_list = []

            for y in range(config.CHUNK_SIZE):

                world_x = config.WORLD_WIDTH * config.CHUNK_SIZE * count + chunk_coordinates[0] * config.CHUNK_SIZE + x 
                world_y = config.WORLD_HEIGHT * config.CHUNK_SIZE * count + chunk_coordinates[1] * config.CHUNK_SIZE + y 

                noise_value = 0
                amplitude = 1
                frequency = 1
                maximum_amplitude = 0

                for _ in range(layers):
                    noise_value += self.__perlin_noise.noise2D(world_x / period * frequency, world_y / period * frequency) * amplitude
                    maximum_amplitude += amplitude
                    amplitude *= 0.5
                    frequency *= 2

                noise_value /= maximum_amplitude

                x_list.append(noise_value)

            noise.append(x_list)

        return noise

    
    def __apply_noise_to_chunk(self, chunk: Chunk, chunk_coordinates: tuple, tile_id: int, noise_values: list, threshold: float, tiles_replaced: tuple, can_generate_here: list | None = None) -> None:

        for x in range(config.CHUNK_SIZE):
            for y in range(config.CHUNK_SIZE):

                world_x = chunk_coordinates[0] * config.CHUNK_SIZE + x 
                world_y = chunk_coordinates[1] * config.CHUNK_SIZE + y 

                if world_y >= self.__surface_heights[world_x]:
                    noise_value = noise_values[x][y]

                    if abs(noise_value) <= threshold and chunk.get_tile_id((x, y)) in tiles_replaced:

                        if can_generate_here is None:
                            chunk.change_tile((x, y), tile_id, False)

                        else:
                            if can_generate_here[x][y]:
                                chunk.change_tile((x, y), tile_id, False)


    def __generate_ore_thresholds(self) -> dict:

        ore_thresholds = {}

        for tile_id in self.__tile_data:

            ore_data = self.__tile_data[tile_id]

            if "ore_threshold" in ore_data:
                ore_thresholds[tile_id] = ore_data["ore_threshold"]

        return ore_thresholds


    def __generate_caves(self, chunk: Chunk, chunk_coordinates: tuple) -> None:

        noise_values = self.__generate_noise_for_chunk(chunk_coordinates, 100, 2, -1)
        self.__apply_noise_to_chunk(chunk, chunk_coordinates, -1, noise_values, config.CAVE_THRESHOLD, (0, 1))


    def __generate_ores(self, chunk: Chunk, chunk_coordinates: tuple) -> None:

        can_generate_here = self.__generate_noise_for_chunk(chunk_coordinates, 25, 1, -2)

        for x in range(config.CHUNK_SIZE):
            for y in range(config.CHUNK_SIZE):

                if abs(can_generate_here[x][y]) <= 0.1:
                    can_generate_here[x][y] = True

                else:
                    can_generate_here[x][y] = False

        thresholds = self.__generate_ore_thresholds()

        for count, tile_id in enumerate(thresholds):

            noise_values = self.__generate_noise_for_chunk(chunk_coordinates, 25, 2, count)
            self.__apply_noise_to_chunk(chunk, chunk_coordinates, int(tile_id), noise_values, thresholds[tile_id], (1,), can_generate_here)


    # CHUNK QUEUE

    def __queue_chunk(self, chunk_coordinates: tuple) -> None:
        if chunk_coordinates in self.__chunks:
            return

        if chunk_coordinates in self.__chunk_queue:
            return

        self.__chunk_queue.append(chunk_coordinates)


    def process_chunk_queue(self, rect, maximum_chunks: int) -> None:
        for _ in range(maximum_chunks):

            if len(self.__chunk_queue) == 0:
                return

            (rect_x, rect_y) = self.which_chunk((rect.centerx // config.TILE_SIZE, rect.centery // config.TILE_SIZE))
            chunk_coordinates = self.__chunk_queue.pop(0)

            while abs(chunk_coordinates[0] - rect_x) > config.UNLOAD_DISTANCE or abs(chunk_coordinates[1] - rect_y) > config.UNLOAD_DISTANCE:

                if len(self.__chunk_queue) == 0:
                    return
                
                chunk_coordinates = self.__chunk_queue.pop(0)

            if chunk_coordinates not in self.__chunks:
                self.__chunks[chunk_coordinates] = self.__generate_chunk(chunk_coordinates)


    def queue_nearby_chunks(self, rect) -> None:

        world_x = rect.centerx // config.TILE_SIZE
        world_y = rect.centery // config.TILE_SIZE

        current_chunk = self.which_chunk((world_x, world_y))

        for x in range(config.LOAD_DISTANCE + 1):
            for y in range(config.LOAD_DISTANCE + 1):

                chunk_coordinates = (current_chunk[0] + x, current_chunk[1] + y)
                self.__queue_chunk(chunk_coordinates)

                chunk_coordinates = (current_chunk[0] - x, current_chunk[1] + y)
                self.__queue_chunk(chunk_coordinates)

                chunk_coordinates = (current_chunk[0] + x, current_chunk[1] - y)
                self.__queue_chunk(chunk_coordinates)

                chunk_coordinates = (current_chunk[0] - x, current_chunk[1] - y)
                self.__queue_chunk(chunk_coordinates)


    # COORDINATES AND QUERIES

    def which_chunk(self, world_coordinates: tuple) -> tuple:
        """Returns chunk coordinates based on world coordinates."""
        return (world_coordinates[0] // config.CHUNK_SIZE, world_coordinates[1] // config.CHUNK_SIZE)


    def where_in_chunk(self, world_coordinates: tuple) -> tuple:
        """Returns tile coordinates in chunk based on world coordinates."""
        return (world_coordinates[0] % config.CHUNK_SIZE, world_coordinates[1] % config.CHUNK_SIZE)


    def get_nearby_rects(self, rect, range_x: int, range_y: int) -> list:
        """Returns a list of tile rects around a rect."""

        world_position_x = rect.centerx // config.TILE_SIZE
        world_position_y = rect.centery // config.TILE_SIZE

        nearby = []

        for x in range(-range_x, range_x + 1):
            for y in range(-range_y, range_y + 1):
                chunk_coordinates = self.which_chunk((world_position_x + x, world_position_y + y))
                coordinates_in_chunk = self.where_in_chunk((world_position_x + x, world_position_y + y))

                chunk = self.__chunks.get(chunk_coordinates)

                if chunk is None:
                    continue

                tile_rect = chunk.get_tile_rect(coordinates_in_chunk)
                
                if tile_rect is not None:
                    nearby.append(tile_rect)
        return nearby


    def __get_nearby_chunks(self, rect) -> dict:

        world_position_x = rect.centerx // config.TILE_SIZE
        world_position_y = rect.centery // config.TILE_SIZE

        current_chunk_coordinates = self.which_chunk((world_position_x, world_position_y))

        nearby = {}

        for x in range(-config.RENDER_DISTANCE, config.RENDER_DISTANCE + 1):
            for y in range(-config.RENDER_DISTANCE, config.RENDER_DISTANCE + 1):
                chunk_coordinates = (current_chunk_coordinates[0] + x, current_chunk_coordinates[1] + y)
                # MIGHT NEED CHANGING FOR WHEN PLAYER IS AT EDGE OF WORLD
                chunk = self.__chunks.get(chunk_coordinates)

                if chunk is not None:
                    nearby[chunk_coordinates] = chunk
        return nearby 


    def break_tile(self, coordinates: tuple) -> None:
        chunk_coordinates = self.which_chunk(coordinates)
        coordinates_in_chunk = self.where_in_chunk(coordinates)
        self.__chunks[chunk_coordinates].change_tile(coordinates_in_chunk, -1)


    def render_world(self, player_rect, screen, camera) -> None:
        chunks = self.__get_nearby_chunks(player_rect)

        for chunk in chunks.values():
            chunk.render(screen, camera, self.__tile_data)


    def get_chunk(self, coordinates: tuple) -> list:
        return self.__chunks[coordinates]


    def get_item_id(self, tile_id: str) -> str:
        return self.__tile_data[tile_id]["item_id"]


    def get_chunks(self) -> dict:
        return self.__chunks


    # SAVING AND LOADING

    def save_chunks(self) -> None:

        saved_chunks = {}

        for chunk_coordinates in self.__chunks:

            chunk = self.__chunks[chunk_coordinates]

            if not(chunk.get_modified()):
                continue

            key = f"{chunk_coordinates[0]},{chunk_coordinates[1]}"
            saved_chunks[key] = chunk.get_tiles()

        with open(f"saves/{self.__name}/chunks.json", "w") as file:
            json.dump(saved_chunks, file)


    def __load_saved_chunks(self) -> dict:
        chunks = {}

        path = f"saves/{self.__name}/chunks.json"

        try:
            with open(path, "r") as file:
                file = json.load(file)

            for key in file:
                x, y = map(int, key.split(","))
                chunk = Chunk((x, y), file[key], True)
                chunks[(x, y)] = chunk

        except FileNotFoundError:
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w") as file:
                json.dump({}, file)

        return chunks

            