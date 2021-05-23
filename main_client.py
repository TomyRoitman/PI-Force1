import json
import socket
import threading
import time
from enum import Enum

import cv2

from gui import Gui
from image_processing.distance import DistanceCalculator2
from image_processing.object_detection import ObjectDetector
from image_processing.stereo import StereoDepthMap
from network.communication import TCPStream
from network.protocol import PICommunication
from network.stream_receiver import StreamReceiver

CAMERA_MENU_TEXT = """
[1] Left Camera\n
[2] Right Camera\n
[3] No stream
[4] Back to main menu\n"""
CAR_CONTROL_MENU_TEXT = """
f - forward\n
b - backwards\n
s - stop\n
l - low\n
m - medium\n
h - high\n
tr - turn right\n
tl - turn left\n
q - back to main menu\n"""
CONFIDENCE = 0.75
CONSTANTS_PATH = "constants.json"
DESTINATION_SIZE = (640, 480)
FPS = 24
LOCK = threading.Lock()
MAIN_TCP_SERVER_ADDRESS = ("192.168.1.35", 10001)
MAIN_MENU_TEXT = """
[1] Control car movement\n
[2] Choose stream source\n
[3] Exit\n"""
# STREAM_FRAME_SHAPE = (192, 256, 3)
STEREO_CALIBRATION_FILE = "image_processing/calibration/stereo_cam.yml"
STREAM_FRAME_SHAPE = (192, 256, 3)
STREAM_FRAME_GRID_ROWS = 4
STREAM_FRAME_GRID_COLUMNS = 4
# RECEIVERS = {}
RUNNING = True
THREADS = []
FRAME_QUEUE = []
DEPTH_MAP_QUEUE = []


def initialize_receivers(constants):
    receiver1 = StreamReceiver('0.0.0.0', 5000)
    t1 = threading.Thread(target=receiver1.receive_stream)
    THREADS.append(t1)
    t1.start()

    receiver2 = StreamReceiver('0.0.0.0', 5001)
    t2 = threading.Thread(target=receiver2.receive_stream)
    THREADS.append(t2)
    t2.start()

    return receiver1, receiver2


def create_depth_map():
    depth_map_obj = StereoDepthMap(STEREO_CALIBRATION_FILE)
    while RUNNING:
        ret = False
        LOCK.acquire()
        if FRAME_QUEUE:
            left_frame, right_frame = FRAME_QUEUE.pop(0)
            ret = True
        LOCK.release()
        if ret:
            depth_map = depth_map_obj.get_depth_image(left_frame, right_frame)
            cv2.imshow("Depth Map", depth_map)
            DEPTH_MAP_QUEUE.append(depth_map)
        cv2.waitKey(1)
        time.sleep(1.0 / 24)

def handle_stream(constants):
    global THREADS

    depth_map_thread = threading.Thread(target=create_depth_map)
    depth_map_thread.start()
    LOCK.acquire()
    THREADS.append(depth_map_thread)
    LOCK.release()
    distance_calculator = DistanceCalculator2()
    receiver1, receiver2 = initialize_receivers(constants)
    detector = ObjectDetector("image_processing/", CONFIDENCE)
    left_results = []
    right_results = []
    while RUNNING:
        current_frames = []
        if receiver1.frame_queue:
            left_ret = True
            left_frame = receiver1.frame_queue.pop(0)
            current_frames.append(left_frame)
            frame, left_results = detector.detect(left_frame)
            h, w = frame.shape[:2]
            cv2.line(frame, (0, int(h / 2) - 2), (w - 1, int(h / 2) - 2), (0, 0, 0), 2)
            cv2.line(frame, (int(w / 2) - 2, 0), (int(w / 2) - 2, h - 1), (0, 0, 0), 2)

            cv2.imshow("Receiver1", left_frame)
        else:
            left_ret = False

        if receiver2.frame_queue:
            right_ret = True
            right_frame = receiver2.frame_queue.pop(0)
            current_frames.append(right_frame)
            frame, right_results = detector.detect(right_frame)
            h, w = frame.shape[:2]
            cv2.line(frame, (0, int(h / 2) - 2), (w - 1, int(h / 2) - 2), (0, 0, 0), 2)
            cv2.line(frame, (int(w / 2) - 2, 0), (int(w / 2) - 2, h - 1), (0, 0, 0), 2)

            cv2.imshow("Receiver2", right_frame)
        else:
            right_ret = False

        if left_ret and right_ret:
            LOCK.acquire()
            FRAME_QUEUE.append(current_frames)
            if DEPTH_MAP_QUEUE:
                depth_map = DEPTH_MAP_QUEUE.pop(0)
                # cv2.imshow("Depth map", depth_map)
            LOCK.release()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # if cv2.waitKey(1) & 0xFF == ord('c'):
        left_results = list(filter(lambda a: "person" in a.label, left_results))
        right_results = list(filter(lambda a: "person" in a.label, right_results))
        if not (left_results and right_results):
            continue

        l_result = left_results[0]
        r_result = right_results[0]
        l_x = (l_result.location[0] + l_result.location[2]) / 2.0
        r_x = (r_result.location[0] + r_result.location[2]) / 2.0
        print("Distance from person: ", distance_calculator.calculate_distance(l_x, r_x))


class Commands(Enum):
    DISCONNECT = PICommunication.disconnect("Exit")  # = Disconnect
    HIGH_SPEED = PICommunication.set_high_speed()  # = Set high speed
    LOW_SPEED = PICommunication.set_low_speed()  # = Set low speed
    MEDIUM_SPEED = PICommunication.set_medium_speed()  # = Set medium speed
    MOVE_FORWARD = PICommunication.move_forward()  # = Move forward
    MOVE_BACKWARDS = PICommunication.move_backwards()  # = Move backwards
    TURN_LEFT =  PICommunication.turn_left()  # = Turn left
    TURN_RIGHT = PICommunication.turn_right()  # = Turn right
    CAMERA_LEFT = PICommunication.move_camera_right()
    CAMERA_RIGHT = PICommunication.move_camera_left()
    CAMERA_UP = PICommunication.move_camera_up()
    CAMERA_DOWN = PICommunication.move_camera_down()
    TOGGLE_DEPTH_MAP = None
    TOGGLE_OBJECT_DETECTION = None
    TOGGLE_DISTANCE = None
    RESET_CAMERA_POSITION = PICommunication.reset_camera_position()


def main():
    global RUNNING
    global THREADS
    constants = json.load(open(CONSTANTS_PATH))
    show_stream_thread = threading.Thread(target=handle_stream, args=(constants,))
    THREADS.append(show_stream_thread)
    show_stream_thread.start()

    server_socket = socket.socket()
    try:
        server_socket.connect(MAIN_TCP_SERVER_ADDRESS)
    except socket.error as e:
        raise socket.error("Could not connect to server. Failed with error:\n" + str(e))

    gui_object = Gui()
    server_tcp_stream = TCPStream(server_socket, 1024, 4, 8, 1024)

    print("[Log] Sending: Request for camera initialization")
    server_tcp_stream.send_by_size(PICommunication.initialize_cameras())

    print("Starting main loop")
    while RUNNING:
        commands = gui_object.get_events()
        for command in commands:
            if command == Commands.TOGGLE_DEPTH_MAP:
                pass
            elif command == Commands.TOGGLE_OBJECT_DETECTION:
                pass
            elif command == Commands.TOGGLE_DISTANCE:
                pass
            elif command == Commands.DISCONNECT:
                server_tcp_stream.send_by_size(PICommunication.disconnect("Exit"))
                server_socket.close()
                break
            else:
                server_tcp_stream.send_by_size(command.value)
        if not RUNNING:
            break
    LOCK.acquire()
    RUNNING = False
    LOCK.release()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
