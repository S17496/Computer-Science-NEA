import world_file as w

class Menu:
    def __init__(self):
        return 

    def menu(self) -> None:
        choice = input()

        if choice == "Create world":
            self.create_world()
        

    def create_world(self) -> w.World:
        name = input()
        seed = input()
        size = input()
        back = input()

        if back == "Yes":
            self.menu()
        return w.World(seed)



