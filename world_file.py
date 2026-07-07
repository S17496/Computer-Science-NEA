import pygame
import config_file as c
import tile_file as t

class World:
    # Constructor
    def __init__(self, world_data):
        self._tile_group = pygame.sprite.Group()
        self._tile_dic = {}
        self.load(world_data)
    
    # Load world
    def load(self, world_data):
        # Create a sprite group and dictionary for tiles
        for row_index, row in enumerate(world_data):
            for col_index, tile in enumerate(row):
                if tile == 1:
                    new_tile = t.Tile(col_index * c.TILE_SIZE, row_index * c.TILE_SIZE)
                    self._tile_group.add(new_tile)
                    self._tile_dic[(col_index, row_index)] = new_tile

    # Get nearby tiles to player
    def get_nearby(self, rect):
        position_x = rect.centerx // c.TILE_SIZE
        position_y = rect.centery // c.TILE_SIZE
        nearby = []
        for i in range(position_x - 2, position_x + 3):
            for j in range(position_y - 2, position_y + 3):
                if (i,j) in self._tile_dic:
                    nearby.append(self._tile_dic[(i,j)])
        return nearby
