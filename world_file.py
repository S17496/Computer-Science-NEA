import pygame
import config_file as c
import tile_file as t

class World:
    # Constructor
    def __init__(self, world_data):
        self.tile_group = pygame.sprite.Group()
        self.tile_dic = {}
        self.load(world_data)
    
    # Load world
    def load(self, world_data):
        # Create a sprite group and dictionary for tiles
        for row_index, row in enumerate(world_data):
            for col_index, tile in enumerate(row):
                if tile == 1:
                    new_tile = t.Tile(col_index * c.TILE_SIZE, row_index * c.TILE_SIZE)
                    self.tile_group.add(new_tile)
                    self.tile_dic[(col_index, row_index)] = new_tile