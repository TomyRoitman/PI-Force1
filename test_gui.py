import cv2
import pygame


class Gui:
    UPPER_BORDER = 0.7
    LOWER_BORDER = -0.7

    def __init__(self):
        pygame.init()
        print("init")
        (width, height) = (1600, 800)
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.flip()
        pygame.joystick.init()
        self.controllers = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        print(f"Detected {len(self.controllers)} controlles")

    def get_surfaces(self):
        a = pygame.Surface((640, 480))
        b = pygame.Surface((640, 480))
        c = pygame.Surface((640, 480))
        return a, b, c


def main():
    gui = Gui()
    screen = gui.screen
    cap = cv2.VideoCapture(0)
    surfaces = gui.get_surfaces()
    left_surf = surfaces[0]
    while True:
        ret, frame = cap.read()
        if ret:
            frame_for_blit = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            left_surf = pygame.surfarray.make_surface(frame_for_blit)
            screen.fill((255, 255, 255))
            screen.blit(left_surf, (0, 0))
        pygame.display.flip()
        pygame.event.get()


if __name__ == '__main__':
    main()
