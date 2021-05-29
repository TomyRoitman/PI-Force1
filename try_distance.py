import math


class Frame_Angles:
    # ------------------------------
    # User Instructions
    # ------------------------------

    # Set the pixel width and height.
    # Set the angle width (and angle height if it is disproportional).
    # These can be set during init, or afterwards.

    # Run build_frame.

    # Use angles_from_center(self,x,y,top_left=True,degrees=True) to get x,y angles from center.
    # If top_left is True, input x,y pixels are measured from the top left of frame.
    # If top_left is False, input x,y pixels are measured from the center of the frame.
    # If degrees is True, returned angles are in degrees, otherwise radians.
    # The returned x,y angles are always from the frame center, negative is left,down and positive is right,up.

    # Use pixels_from_center(self,x,y,degrees=True) to convert angle x,y to pixel x,y (always from center).
    # This is the reverse of angles_from_center.
    # If degrees is True, input x,y should be in degrees, otherwise radians.

    # Use frame_add_crosshairs(frame) to add crosshairs to a frame.
    # Use frame_add_degrees(frame) to add 10 degree lines to a frame (matches target).
    # Use frame_make_target(openfile=True) to make an SVG image target and open it (matches frame with degrees).

    # ------------------------------
    # User Variables
    # ------------------------------

    pixel_width = 640
    pixel_height = 480

    angle_width = 60
    angle_height = None

    # ------------------------------
    # System Variables
    # ------------------------------

    x_origin = None
    y_origin = None

    x_adjacent = None
    x_adjacent = None

    # ------------------------------
    # Init Functions
    # ------------------------------

    def __init__(self, pixel_width=None, pixel_height=None, angle_width=None, angle_height=None):

        # full frame dimensions in pixels
        if type(pixel_width) in (int, float):
            self.pixel_width = int(pixel_width)
        if type(pixel_height) in (int, float):
            self.pixel_height = int(pixel_height)

        # full frame dimensions in degrees
        if type(angle_width) in (int, float):
            self.angle_width = float(angle_width)
        if type(angle_height) in (int, float):
            self.angle_height = float(angle_height)

        # do initial setup
        self.build_frame()

    def build_frame(self):

        # this assumes correct values for pixel_width, pixel_height, and angle_width

        # fix angle height
        if not self.angle_height:
            self.angle_height = self.angle_width * (self.pixel_height / self.pixel_width)

        # center point (also max pixel distance from origin)
        self.x_origin = int(self.pixel_width / 2)
        self.y_origin = int(self.pixel_height / 2)

        # theoretical distance in pixels from camera to frame
        # this is the adjacent-side length in tangent calculations
        # the pixel x,y inputs is the opposite-side lengths
        self.x_adjacent = self.x_origin / math.tan(math.radians(self.angle_width / 2))
        self.y_adjacent = self.y_origin / math.tan(math.radians(self.angle_height / 2))

    # ------------------------------
    # Pixels-to-Angles Functions
    # ------------------------------

    def angles(self, x, y):

        return self.angles_from_center(x, y)

    def angles_from_center(self, x, y, top_left=True, degrees=True):

        # x = pixels right from left edge of frame
        # y = pixels down from top edge of frame
        # if not top_left, assume x,y are from frame center
        # if not degrees, return radians

        if top_left:
            x = x - self.x_origin
            y = self.y_origin - y

        xtan = x / self.x_adjacent
        ytan = y / self.y_adjacent

        xrad = math.atan(xtan)
        yrad = math.atan(ytan)

        if not degrees:
            return xrad, yrad

        return math.degrees(xrad), math.degrees(yrad)

    def pixels_from_center(self, x, y, degrees=True):

        # this is the reverse of angles_from_center

        # x = horizontal angle from center
        # y = vertical angle from center
        # if not degrees, angles are radians

        if degrees:
            x = math.radians(x)
            y = math.radians(y)

        return int(self.x_adjacent * math.tan(x)), int(self.y_adjacent * math.tan(y))

    # ------------------------------
    # 3D Functions
    # ------------------------------

    def distance(self, *coordinates):
        return self.distance_from_origin(*coordinates)

    def distance_from_origin(self, *coordinates):
        return math.sqrt(sum([x ** 2 for x in coordinates]))

    def intersection(self, pdistance, langle, rangle, degrees=False):

        # return (X,Y) of target from left-camera-center

        # pdistance is the measure from left-camera-center to right-camera-center (point-to-point, or point distance)
        # langle is the left-camera  angle to object measured from center frame (up/right positive)
        # rangle is the right-camera angle to object measured from center frame (up/right positive)
        # left-camera-center is origin (0,0) for return (X,Y)
        # X is measured along the baseline from left-camera-center to right-camera-center
        # Y is measured from the baseline

        # fix degrees
        if degrees:
            langle = math.radians(langle)
            rangle = math.radians(rangle)

        # fix angle orientation (from center frame)
        # here langle is measured from right baseline
        # here rangle is measured from left  baseline
        langle = math.pi / 2 + langle
        rangle = math.pi / 2 - rangle

        # all calculations using tangent
        if langle == 0:
            langle = 0.1
        ltan = math.tan(langle)
        if rangle == 0:
            rangle = 0.1
        rtan = math.tan(rangle)

        # get Y value
        # use the idea that pdistance = ( Y/ltan + Y/rtan )
        Y = pdistance / (1 / ltan + 1 / rtan)

        # get X measure from left-camera-center using Y
        X = Y / ltan

        # done
        return X, Y

    def location(self, pdistance, lcamera, rcamera, center=False, degrees=True):

        # return (X,Y,Z,D) of target from left-camera-center (or baseline midpoint if center-True)

        # pdistance is the measure from left-camera-center to right-camera-center (point-to-point, or point distance)
        # lcamera = left-camera-center (Xangle-to-target,Yangle-to-target)
        # rcamera = right-camera-center (Xangle-to-target,Yangle-to-target)
        # left-camera-center is origin (0,0) for return (X,Y)
        # X is measured along the baseline from left-camera-center to right-camera-center
        # Y is measured from the baseline
        # Z is measured vertically from left-camera-center (should be same as right-camera-center)
        # D is distance from left-camera-center (based on pdistance units)

        # separate values
        lxangle, lyangle = lcamera
        rxangle, ryangle = rcamera

        # yangle should be the same for both cameras (if aligned correctly)
        yangle = (lyangle + ryangle) / 2

        # fix degrees
        if degrees:
            lxangle = math.radians(lxangle)
            rxangle = math.radians(rxangle)
            yangle = math.radians(yangle)

        # get X,Z (remember Y for the intersection is Z frame)
        X, Z = self.intersection(pdistance, lxangle, rxangle, degrees=False)

        # get Y
        # using yangle and 2D distance to target
        Y = math.tan(yangle) * self.distance_from_origin(X, Z)

        # baseline-center instead of left-camera-center
        if center:
            X -= pdistance / 2

        # get 3D distance
        D = self.distance_from_origin(X, Y, Z)

        # done
        return X, Y, Z, D


class DistanceCalculator3:

    def __init__(self):
        # cameras are the same, so only 1 needed
        pixel_width, pixel_height, angle_width, angle_height = 640, 480, 40, 40 * (480 / 640)
        self.angler = Frame_Angles(pixel_width, pixel_height, angle_width, angle_height)
        self.angler.build_frame()

    def calculate_distance(self, x1m, y1m, x2m, y2m):
        # get angles from camera centers
        xlangle, ylangle = self.angler.angles_from_center(x1m, y1m, top_left=False, degrees=True)
        xrangle, yrangle = self.angler.angles_from_center(x2m, y2m, top_left=False, degrees=True)

        # triangulate
        X, Y, Z, D = self.angler.location(4.7, (xlangle, ylangle), (xrangle, yrangle),
                                          center=True, degrees=True)
        return X, Y, Z, D


def run():
    # ------------------------------
    # full error catch
    # ------------------------------
    try:

        # cameras are the same, so only 1 needed
        pixel_width, pixel_height, angle_width, angle_height = 640, 480, 40, 40
        angler = Frame_Angles(pixel_width, pixel_height, angle_width, angle_height)
        angler.build_frame()
        klen = 3  # length of target queues, positive target frames required to reset set X,Y,Z,D
        x1k, y1k, x2k, y2k = [], [], [], []
        x1m, y1m, x2m, y2m = 0, 0, 0, 0

        # loop
        while 1:
            left_location = [217, 32, 319, 356]
            l_start_x, l_start_y, l_end_x, l_end_y = left_location
            x1m = (l_start_x + l_end_x) / 2
            y1m = (l_start_y + l_end_y) / 2
            right_location = [62, 68, 174, 416]
            r_start_x, r_start_y, r_end_x, r_end_y = right_location
            x2m = (r_start_x + r_end_x) / 2
            y2m = (r_start_y + r_end_y) / 2

            # x1m, y1m, x2m, y2m = [208.5,
            #                       231.0,
            #                       269.5,
            #                       231.0]

            # x1m, y1m, x2m, y2m = [202.0, 233.0, 274.5, 233.0]
            # x1m, y1m, x2m, y2m = [4 , 4 , 16 , 3]
            x1m, y1m, x2m, y2m = [191.5, 167.0, 306.5, 239.5]

            # get angles from camera centers
            xlangle, ylangle = angler.angles_from_center(x1m, y1m, top_left=True, degrees=True)
            xrangle, yrangle = angler.angles_from_center(x2m, y2m, top_left=True, degrees=True)

            # triangulate
            X, Y, Z, D = angler.location(4.7, (xlangle, ylangle), (xrangle, yrangle),
                                         center=True, degrees=True)

            print(X, Y, Z, D)
            exit()
            # # display coordinate data
            # fps1 = int(ct1.current_frame_rate)
            # fps2 = int(ct2.current_frame_rate)
            # text = 'X: {:3.1f}\nY: {:3.1f}\nZ: {:3.1f}\nD: {:3.1f}\nFPS: {}/{}'.format(X, Y, Z, D, fps1, fps2)
            # lineloc = 0
            # lineheight = 30
            # for t in text.split('\n'):
            #     lineloc += lineheight
            #     cv2.putText(frame1,
            #                 t,
            #                 (10, lineloc),  # location
            #                 cv2.FONT_HERSHEY_PLAIN,  # font
            #                 # cv2.FONT_HERSHEY_SIMPLEX, # font
            #                 1.5,  # size
            #                 (0, 255, 0),  # color
            #                 1,  # line width
            #                 cv2.LINE_AA,  #
            #                 False)  #
            #
            # # display current target
            # if x1k:
            #     targeter1.frame_add_crosshairs(frame1, x1m, y1m, 48)
            #     targeter2.frame_add_crosshairs(frame2, x2m, y2m, 48)
            #
            #     # display frame
            # cv2.imshow("Left Camera 1", frame1)
            # cv2.imshow("Right Camera 2", frame2)
            #
            # # detect keys
            # key = cv2.waitKey(1) & 0xFF
            # if cv2.getWindowProperty('Left Camera 1', cv2.WND_PROP_VISIBLE) < 1:
            #     break
            # elif cv2.getWindowProperty('Right Camera 2', cv2.WND_PROP_VISIBLE) < 1:
            #     break
            # elif key == ord('q'):
            #     break
            # elif key != 255:
            #     print('KEY PRESS:', [chr(key)])

    # ------------------------------
    # full error catch
    # ------------------------------
    except Exception as e:
        print(e)

    # done
    print('DONE')


if __name__ == '__main__':
    run()
