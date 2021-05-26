import math


class DistanceCalculator:
    DISTANCE_BETWEEN_CAMERAS = 0.0465
    CAMERA_VIEW_ANGLE = 20.04
    PIXEL_WIDTH = 640

    def __init__(self, A: float = 0.0465, omega1: float = 20.04 * 2, omega2: float = 20.904 * 2,
                 frame_width: int = 640):
        self.A = A
        self.omega1 = omega1
        self.omega2 = omega2
        self.H1 = frame_width
        self.H2 = self.H1
        self.beta1 = (180 - self.omega1) / 2
        self.beta2 = (180 - self.omega2) / 2

    def calculate_distance(self, P1, P2):
        phi = (P1 / self.H1) * self.omega1 + self.beta1
        theta = (P2 / self.H2) * self.omega2 + self.beta2
        return (self.A * self.sinus(theta) * self.sinus(phi)) / self.sinus(180 - (theta + phi))

    def sinus(self, angle):
        return math.sin(angle / 180 * math.pi)


class DistanceCalculator2:
    DISTANCE_BETWEEN_CAMERAS = 0.047
    PIXEL_WIDTH = 640

    def __init__(self, l: float = 0.047, omegal: float = 20.32 * 2, omegar: float = 20.32 * 2,
                 frame_width: int = 640):
        self.l = l
        self.omegal = omegal
        self.omegar = omegar
        self.Hl = frame_width
        self.Hr = self.Hl
        self.d_l = self.Hl / math.tan(math.radians(self.omegal / 2))
        self.d_r = self.Hr / math.tan(math.radians(self.omegar / 2))

    def calculate_distance(self, x_l, x_r):
        angle_l = math.radians(90 - math.degrees(math.atan((x_l - self.Hl / 2) / self.d_l)))
        tan_l = math.tan(angle_l)

        angle_r = math.radians(90 - math.degrees(math.atan((self.Hr / 2 - x_r) / self.d_r)))
        tan_r = math.tan(angle_r)

        to_return = -1
        try:
            if x_r > self.Hr / 2:
                to_return = (self.l * tan_l * math.tan(math.pi - angle_r)) / (math.tan(math.pi - angle_r) - tan_l)
            elif x_l < self.Hl / 2:
                to_return = (self.l * tan_r * math.tan(math.pi - angle_l)) / (math.tan(math.pi - angle_l) - tan_r)
            else:
                to_return = (self.l * tan_l * tan_r) / (tan_l + tan_r)
            return to_return
        except:
            return to_return

    def sinus(self, angle):
        return math.sin(angle / 180 * math.pi)

    def to_radian(self, angle):
        return float(angle) / 180 * math.pi


def main():
    distance_calculator = DistanceCalculator()
    left_location = [217, 32, 319, 356]
    l_start_x, l_start_y, l_end_x, l_end_y = left_location
    right_location = [62, 68, 174, 416]
    r_start_x, r_start_y, r_end_x, r_end_y = right_location
    left_middle_x = (l_start_x + l_end_x) / 2
    right_middle_x = (r_start_x + r_end_x) / 2
    P1 = 640 - left_middle_x
    P2 = right_middle_x
    dist = distance_calculator.calculate_distance(P1, P2)
    print(dist)


def main2():
    distance_calculator = DistanceCalculator2()
    left_location = [217, 32, 319, 356]
    l_start_x, l_start_y, l_end_x, l_end_y = left_location
    right_location = [62, 68, 174, 416]
    r_start_x, r_start_y, r_end_x, r_end_y = right_location
    # left_middle_x = (l_start_x + l_end_x) / 2
    left_middle_x = 640 - 153
    # right_middle_x = (r_start_x + r_end_x) / 2
    right_middle_x = 640 - 296

    dist = distance_calculator.calculate_distance(left_middle_x, right_middle_x)
    print(dist)


if __name__ == '__main__':
    main2()
