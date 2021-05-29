import sys
from enum import Enum

import pygame

from network.protocol import PICommunication


class Commands(Enum):
    """
    Contains all commands, and translates them to messages
    """
    DISCONNECT = PICommunication.disconnect("Exit")  # = Disconnect
    HIGH_SPEED = PICommunication.set_high_speed()  # = Set high speed
    LOW_SPEED = PICommunication.set_low_speed()  # = Set low speed
    MEDIUM_SPEED = PICommunication.set_medium_speed()  # = Set medium speed
    MOVE_FORWARD = PICommunication.move_forward()  # = Move forward
    MOVE_BACKWARDS = PICommunication.move_backwards()  # = Move backwards
    TURN_LEFT = PICommunication.turn_left()  # = Turn left
    TURN_RIGHT = PICommunication.turn_right()  # = Turn right
    CAMERA_LEFT = PICommunication.move_camera_right()
    CAMERA_RIGHT = PICommunication.move_camera_left()
    CAMERA_UP = PICommunication.move_camera_up()
    CAMERA_DOWN = PICommunication.move_camera_down()
    TOGGLE_DEPTH_MAP = None
    TOGGLE_OBJECT_DETECTION = None
    TOGGLE_DISTANCE = None
    RESET_CAMERA_POSITION = PICommunication.reset_camera_position()
    STOP = PICommunication.stop()

class Gui:
    UPPER_BORDER = 0.7
    LOWER_BORDER = -0.7

    def __init__(self):
        """
        Initialize pygame gui.
        controllers: list contains all controllers connected to pc
        car_horizontal, car_vertical, camera_horizontal,camera_vertical -> bool, indicate if motion is already requested
        in that axis
        """
        pygame.init()
        print("init")
        (width, height) = (1600, 800)
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.flip()
        pygame.joystick.init()
        background_image = pygame.image.load("background.jpg")
        self.screen.blit(background_image, (0, 0))
        self.controllers = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        print(f"Detected {len(self.controllers)} controlles")
        self.right = False
        self.left = False
        self.forward = False
        self.backwards = False

        self.car_horizontal = False
        self.car_vertical = False
        self.camera_horizontal = False
        self.camera_vertical = False

    def get_events(self):
        """
        :return: Parse pygame events and return a list of commands requested by user
        """

        controller = self.controllers[0]
        commands = []

        if not controller:
            return commands

        left_joystick_axes = {i: controller.get_axis(i) for i in range(0, 2)}
        l = list(left_joystick_axes.items())
        l.sort(key=lambda item: abs(item[1]), reverse=True)
        if l:
            biggest_left = l[0]
            # if len(left_joystick_axes) > 0:

            # Left horizontal
            if biggest_left[0] == 0:
                if biggest_left[1] > Gui.UPPER_BORDER:
                    commands.append(Commands.TURN_RIGHT)
                    self.car_horizontal = True
                elif biggest_left[1] < Gui.LOWER_BORDER:
                    commands.append(Commands.TURN_LEFT)
                    self.car_horizontal = True
                elif self.car_horizontal:
                    commands.append(Commands.STOP)
                    self.car_horizontal = False

            # Left vertical
            elif biggest_left[0] == 1:
                if biggest_left[1] > Gui.UPPER_BORDER:
                    commands.append(Commands.MOVE_BACKWARDS)
                    self.car_vertical = True
                elif biggest_left[1] < Gui.LOWER_BORDER:
                    commands.append(Commands.MOVE_FORWARD)
                    self.car_vertical = True
                elif self.car_vertical:
                    commands.append(Commands.STOP)
                    self.car_vertical = False

        right_joystick_axes = {i: controller.get_axis(i) for i in range(2, 4)}
        l = list(right_joystick_axes.items())
        l.sort(key=lambda item: abs(item[1]), reverse=True)
        if l:
            # if len(right_joystick_axes) > 0:

            biggest_right = l[0]

            # Right horizontal
            if biggest_right[0] == 2:
                if biggest_right[1] > Gui.UPPER_BORDER:
                    commands.append(Commands.CAMERA_RIGHT)
                    self.camera_horizontal = True
                elif biggest_right[1] < Gui.LOWER_BORDER:
                    commands.append(Commands.CAMERA_LEFT)
                    self.camera_horizontal = True
                elif self.camera_horizontal:
                    commands.append(Commands.STOP)
                    self.camera_horizontal = False

            # Right vertical
            elif biggest_right[0] == 3:
                if biggest_right[1] > Gui.UPPER_BORDER:
                    commands.append(Commands.CAMERA_DOWN)
                    self.camera_vertical = True
                elif biggest_right[1] < Gui.LOWER_BORDER:
                    commands.append(Commands.CAMERA_UP)
                    self.camera_vertical = True
                elif self.camera_vertical:
                    commands.append(Commands.STOP)
                    self.camera_vertical = False

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:
                    commands.append(Commands.TOGGLE_DISTANCE)
                elif event.button == 3:
                    commands.append(Commands.TOGGLE_DISTANCE.RESET_CAMERA_POSITION)
                elif event.button == 4:
                    commands.append(Commands.TOGGLE_DEPTH_MAP)
                elif event.button == 5:
                    commands.append(Commands.TOGGLE_OBJECT_DETECTION)
                elif event.button == 7:
                    commands.append(Commands.DISCONNECT)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        return commands


def main():
    gui = Gui()
    gui.run()


if __name__ == '__main__':
    main()
