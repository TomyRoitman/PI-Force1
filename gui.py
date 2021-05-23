import pygame

from network.protocol import PICommunication


class Gui:
    MINIMAL_VALUE = 0.7

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.controllers = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        print(f"Detected {len(self.controllers)} controlles")

    def get_events(self):

        controller = self.controllers[0]
        commands = []

        if not controller:
            return commands

        left_joystick_axes = {i: controller.get_axis(i) for i in range(0, 2)}
        biggest_left = left_joystick_axes.items().sort(key=lambda item: abs(item[1]), reverse=True)[0]

        # Left horizontal
        if biggest_left[0] == 0:
            if biggest_left[1] > Gui.MINIMAL_VALUE:
                duration = 0
                commands.append(PICommunication.turn_right(float(duration)))
            elif biggest_left < -Gui.MINIMAL_VALUE:
                duration = 0
                commands.append(PICommunication.turn_left(float(duration)))

        # Left vertical
        elif biggest_left[0] == 1:
            if biggest_left[1] > Gui.MINIMAL_VALUE:
                commands.append(PICommunication.move_backwards())
            elif biggest_left < -Gui.MINIMAL_VALUE:
                commands.append(PICommunication.move_forward())

        right_joystick_axes = {i: controller.get_axis(i) for i in range(2, 4)}
        biggest_right = list(right_joystick_axes.items()).sort(key=lambda item: abs(item[1]), reverse=True)[0]

        # Right horizontal
        if biggest_right[0] == 2:
            if biggest_right[1] > Gui.MINIMAL_VALUE:
                commands.append(PICommunication.move_camera_right())
            elif biggest_right < -Gui.MINIMAL_VALUE:
                commands.append(PICommunication.move_camera_left())

        # Right vertical
        elif biggest_right[0] == 3:
            if biggest_right[1] > Gui.MINIMAL_VALUE:
                commands.append(PICommunication.move_camera_down())
            elif biggest_right < -Gui.MINIMAL_VALUE:
                commands.append(PICommunication.move_camera_up())

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:
                    commands.append(PICommunication.toggle_distance())
                elif event.button == 3:
                    commands.append(PICommunication.reset_camera_position())
                elif event.button == 4:
                    commands.append(PICommunication.toggle_depth_map())
                elif event.button == 5:
                    commands.append(PICommunication.toggle_object_detection())
                elif event.button == 7:
                    commands.append(PICommunication.disconnect())

        return commands


def main():
    gui = Gui()
    gui.run()


if __name__ == '__main__':
    main()
