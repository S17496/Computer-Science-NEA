import pygame
import items
import config



class EventHandler:
    def __init__(self, player, world, camera, drop_tile, drop_item, inventory_ui, crafting_ui):
        self.__player = player
        self.__world = world 
        self.__camera = camera 
        self.__drop_tile = drop_tile
        self.__drop_item = drop_item
        self.__inventory_ui = inventory_ui
        self.__crafting_ui = crafting_ui
        self.__break_target = None 
        self.__break_start = None 
        self.__inventory_click = False

    def reset_mining(self) -> None:
        self.__break_target = None 
        self.__break_start = None 

    def handle_slot_switching(self, event) -> None:
        slot_num = (event.key - 39) % 10
        self.__player.get_inventory().set_selected_slot(slot_num)

    def handle_inventory_state(self) -> None:
        if self.__inventory_ui.is_open() and self.__player.get_hand() is not None:
            self.__drop_item(self.__player.rect.right, self.__player.rect.y, self.__player.get_hand())
            self.__player.set_hand(None)

        self.__inventory_ui.change_state()

    def handle_inventory_click(self, event) -> None:
        if not self.__inventory_ui.is_open() or event.button != 1:
            return

        slot = self.__inventory_ui.get_slot_at_position(event.pos)

        if slot is not None:
            self.__player.swap_hand_item(slot)
            self.__inventory_click = True

    def handle_key_event(self, event) -> None:
        if event.key in range(48, 58):
            self.handle_slot_switching(event)
        elif event.key == pygame.K_e:
            self.handle_inventory_state()


    def handle_hold_right_click(self) -> None:

        player_pos1 = self.__player.get_top_left_coordinates()
        player_pos2 = self.__player.get_bottom_right_coordinates()

        if not isinstance(self.__player.get_inventory().get_selected_item(), items.TileItem):
            return 
        
        mouse_pos = pygame.mouse.get_pos()
        tile_coordinates = (int((mouse_pos[0] + self.__camera.get_x())//config.TILE_SIZE), int((mouse_pos[1] + self.__camera.get_y())//config.TILE_SIZE))

        if tile_coordinates[0] >= player_pos1[0] and tile_coordinates[0] <= player_pos2[0] and tile_coordinates[1] >= player_pos1[1] and tile_coordinates[1] <= player_pos2[1]:
            return 
        
        chunk_coordinates = self.__world.which_chunk(tile_coordinates)
        coordinates_in_chunk = self.__world.where_in_chunk(tile_coordinates)

        if chunk_coordinates not in self.__world.get_chunks():
            return

        chunk = self.__world.get_chunk(chunk_coordinates)

        if chunk.get_tile_id(coordinates_in_chunk) >= 0:
            return 

        item = self.__player.get_inventory().get_selected_item()
        item.set_quantity(item.get_quantity()-1)
        chunk.change_tile(coordinates_in_chunk, int(item.get_id()))


    def __handle_crafting(self) -> None:

        mouse_pos = pygame.mouse.get_pos()

        slot = self.__crafting_ui.get_slot_at_position(mouse_pos, self.__inventory_ui)

        if slot is None:
            return

        


    def handle_hold_left_click(self) -> None:
        # Breaking blocks
        
        selected_item = self.__player.get_inventory().get_selected_item()
        
        if not isinstance(selected_item, items.Pickaxe):
            self.reset_mining()
            return 
            
        mouse_pos = pygame.mouse.get_pos()
        tile_coordinates = (int((mouse_pos[0] + self.__camera.get_x())//config.TILE_SIZE), int((mouse_pos[1] + self.__camera.get_y())//config.TILE_SIZE))
        
        chunk_coordinates = self.__world.which_chunk(tile_coordinates)
        coordinates_in_chunk = self.__world.where_in_chunk(tile_coordinates)
        
        if chunk_coordinates not in self.__world.get_chunks():
            self.reset_mining()
            return
            
        tile_id = self.__world.get_chunk(chunk_coordinates).get_tile_id(coordinates_in_chunk)
        
        if tile_id < 0:
            self.reset_mining()
            return
        
        item_id = self.__world.get_item_id(str(tile_id))
        
        break_time = int(1000 / selected_item.get_pickaxe_speed())
          
        if self.__break_start is None or tile_coordinates != self.__break_target:
            self.__break_start = pygame.time.get_ticks()
            self.__break_target = tile_coordinates
        
        elapsed = pygame.time.get_ticks() - self.__break_start
            
        if elapsed >= break_time and self.__break_target != None:
            self.__drop_tile(tile_coordinates, item_id)
            self.__world.break_tile(tile_coordinates)
            self.reset_mining()

            

    def handle_events(self) -> bool:

        self.__inventory_click = False

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_key_event(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_inventory_click(event)

        if pygame.mouse.get_pressed()[0] and not self.__inventory_click:
            self.handle_hold_left_click()
        else:
            self.reset_mining()

        if pygame.mouse.get_pressed()[2]:
            self.handle_hold_right_click()

        return True  # Keeps main loop running