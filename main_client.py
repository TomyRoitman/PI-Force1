import json
import socket
import threading
import time
from enum import Enum

import cv2

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
        LOCK.acquire()
        if FRAME_QUEUE:
            left_frame, right_frame = FRAME_QUEUE.pop(0)
            DEPTH_MAP_QUEUE.append(depth_map_obj.get_depth_image(left_frame, right_frame))
        LOCK.release()
        # time.sleep(1.0 / 60)
        # cv2.waitKey(1)

def handle_stream(constants):
    global THREADS

    depth_map_thread = threading.Thread(target=create_depth_map)
    depth_map_thread.start()
    LOCK.acquire()
    THREADS.append(depth_map_thread)
    LOCK.release()

    receiver1, receiver2 = initialize_receivers(constants)
    detector = ObjectDetector("image_processing/", CONFIDENCE)
    left_ret = False
    right_frame = False

    while RUNNING:

        if receiver1.frame_queue:
            left_ret = True
            left_frame = receiver1.frame_queue.pop(0)
            # results = detector.detect(frame)
            # cv2.imshow("Receiver1", left_frame)
        else:
            left_ret = False

        if receiver2.frame_queue:
            right_ret = True
            right_frame = receiver2.frame_queue.pop(0)
            # results = detector.detect(frame)
            # cv2.imshow("Receiver2", right_frame)
        else:
            right_ret = False

        if left_ret and right_ret:
            # LOCK.acquire()
            FRAME_QUEUE.append((left_frame, right_frame))

            if DEPTH_MAP_QUEUE:
                depth_map = DEPTH_MAP_QUEUE.pop(0)
                cv2.imshow("Depth map", depth_map)
            # cv2.imshow("disparity", depth_map)
            #     print("Showed depth map")
            # LOCK.release()
            # depth_map = depth_map_obj.get_depth_image(left_frame, right_frame)
            # norm_image = cv2.normalize(depth_map, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
            # back_to_rgb = cv2.applyColorMap(depth_map, cv2.COLORMAP_SPRING)

            # cv2.imshow("colored disparity", back_to_rgb)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1.0 / 24)


class StreamOptions(Enum):
    left = 1
    right = 2
    none = 3


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def handle_car_movement_control_menu(server_tcp_stream: TCPStream):
    while RUNNING:
        command = input("Please choose a stream mode from below:\n" + CAR_CONTROL_MENU_TEXT)
        message = None
        if command == "f":
            message = PICommunication.move_forward()
        elif command == "b":
            message = PICommunication.move_backwards()
        elif command == "s":
            message = PICommunication.stop()
        elif command == "l":
            message = PICommunication.set_low_speed()
        elif command == "m":
            message = PICommunication.set_medium_speed()
        elif command == "h":
            message = PICommunication.set_high_speed()
        elif command == "tr":
            duration = 0
            message = PICommunication.turn_right(float(duration))
        elif command == "tl":
            duration = 0
            message = PICommunication.turn_left(float(duration))
        elif command == "q":
            break
        else:
            print(f"Command unknown: {command}\n")
            continue
        if message:
            server_tcp_stream.send_by_size(message)


def handle_stream_source_menu(server_tcp_stream: TCPStream):
    global CAMERA_CHOSEN
    command = input("Please choose a stream mode from below:\n" + CAMERA_MENU_TEXT)
    while RUNNING:
        if command in ("1", "2", "3"):
            # Left, Right or None
            server_tcp_stream.send_by_size(PICommunication.choose_camera(StreamOptions(int(command)).name))
            break
        elif command == "4":
            # Back to main menu
            break
        else:
            print(f"Command unknown: {command}\n")


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
    server_tcp_stream = TCPStream(server_socket, 1024, 4, 8, 1024)

    print("Entering main loop")
    while RUNNING:
        command = input("Please choose an action from below:\n" + MAIN_MENU_TEXT)
        if command == "1":
            handle_car_movement_control_menu(server_tcp_stream)
        elif command == "2":
            handle_stream_source_menu(server_tcp_stream)
        elif command == "3":
            # Disconnect
            server_tcp_stream.send_by_size(PICommunication.disconnect("Exit"))
            server_socket.close()
            break
        else:
            print(f"Command unknown: {command}\n")

    LOCK.acquire()
    RUNNING = False
    LOCK.release()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
