import config

class Camera:
    def __init__(self):
        self.__x = 0
        self.__y = 0

    def move_camera(self, target_x: int, target_y: int, max_x: int, max_y: int) -> None:

        self.__x += (target_x - self.__x) * 0.2
        self.__y += (target_y - self.__y) * 0.2

        camera_max_x = max_x - config.SCREEN_WIDTH
        camera_max_y = max_y - config.SCREEN_HEIGHT

        if self.__x < 0:
            self.__x = 0

        elif self.__x > camera_max_x:
            self.__x = camera_max_x

        if self.__y < 0:
            self.__y = 0

        elif self.__y > camera_max_y:
            self.__y = camera_max_y

    # Getters and setters

    def get_x(self) -> int:
        return round(self.__x)

    def get_y(self) -> int:
        return round(self.__y)