class Camera:
    def __init__(self):
        self.__x = 0
        self.__y = 0

    def move_camera(self, target_x: int, target_y: int) -> None:
        self.__x += (target_x - self.__x) * 0.1
        self.__y += (target_y - self.__y) * 0.1

    # Getters and setters

    def get_x(self) -> int:
        return round(self.__x)

    def get_y(self) -> int:
        return round(self.__y)