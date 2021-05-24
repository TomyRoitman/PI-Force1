import json
import socket
import sys
import threading
import time

import cv2
import numpy as np
import pygame

from gui import Gui, Commands
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
BACKGROUND_COLOR = (255, 255, 255)
SCREEN_DIMENSIONS = [1600, 800]


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
            # cv2.imshow("Depth Map", depth_map)
            DEPTH_MAP_QUEUE.append(depth_map)
        cv2.waitKey(1)
        time.sleep(1.0 / 24)


def blit_frame(screen, frame, size, position):
    frame_blit = cv2.resize(frame, size)
    frame_blit = cv2.flip(frame_blit, 1)  # flip horizontal
    frame_blit = cv2.cvtColor(frame_blit, cv2.COLOR_BGR2RGB)
    frame_blit = np.rot90(frame_blit)
    surface = pygame.surfarray.make_surface(frame_blit)
    screen.blit(surface, position)


def handle_stream(constants, screen):
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
    # screen.fill(BACKGROUND_COLOR)
    while RUNNING:

        current_frames = []
        if receiver1.frame_queue:
            left_ret = True
            LOCK.acquire()
            left_frame = receiver1.frame_queue.pop(0)
            LOCK.release()
            current_frames.append(left_frame)
            frame, left_results = detector.detect(left_frame)

            # h, w = frame.shape[:2]
            # cv2.line(frame, (0, int(h / 2) - 2), (w - 1, int(h / 2) - 2), (0, 0, 0), 2)
            # cv2.line(frame, (int(w / 2) - 2, 0), (int(w / 2) - 2, h - 1), (0, 0, 0), 2)

            blit_frame(screen, left_frame, (640, 480), (SCREEN_DIMENSIONS[0] / 2, 50))

        else:
            left_ret = False

        if receiver2.frame_queue:
            right_ret = True
            right_frame = receiver2.frame_queue.pop(0)
            current_frames.append(right_frame)
            frame, right_results = detector.detect(right_frame)

            # h, w = frame.shape[:2]
            # cv2.line(frame, (0, int(h / 2) - 2), (w - 1, int(h / 2) - 2), (0, 0, 0), 2)
            # cv2.line(frame, (int(w / 2) - 2, 0), (int(w / 2) - 2, h - 1), (0, 0, 0), 2)
            size = (640, 480)
            blit_frame(screen, frame, size, (SCREEN_DIMENSIONS[0] / 2 - size[0], 50))

        else:
            right_ret = False

        if left_ret and right_ret:
            LOCK.acquire()
            FRAME_QUEUE.append(current_frames)
            if DEPTH_MAP_QUEUE:
                depth_map = DEPTH_MAP_QUEUE.pop(0)
                size = (300, 225)
                blit_frame(screen, depth_map, size, ((SCREEN_DIMENSIONS[0] - size[0]) / 2, 550))
            LOCK.release()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        left_results = list(filter(lambda a: "person" in a.label, left_results))
        right_results = list(filter(lambda a: "person" in a.label, right_results))
        if left_results and right_results:
            l_result = left_results[0]
            r_result = right_results[0]
            l_x = (l_result.location[0] + l_result.location[2]) / 2.0
            r_x = (r_result.location[0] + r_result.location[2]) / 2.0
            print("Distance from person: ", distance_calculator.calculate_distance(l_x, r_x))

        # screen.blit(left_surface, (500, 0))
        # screen.blit(right_surface, (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.JOYBUTTONDOWN and event.button == 7):
                pygame.quit()
                sys.exit()
        # time.sleep(1.0 / 24)


def main():
    global RUNNING
    global THREADS
    gui_object = Gui()
    screen = gui_object.screen
    constants = json.load(open(CONSTANTS_PATH))
    show_stream_thread = threading.Thread(target=handle_stream, args=(constants, screen))
    THREADS.append(show_stream_thread)
    show_stream_thread.start()

    server_socket = socket.socket()
    try:
        server_socket.connect(MAIN_TCP_SERVER_ADDRESS)
    except socket.error as e:
        raise socket.error("Could not connect to server. Failed with error:\n" + str(e))

    # time.sleep(7.0)

    server_tcp_stream = TCPStream(server_socket, 1024, 4, 8, 1024)

    print("[Log] Sending: Request for camera initialization")
    server_tcp_stream.send_by_size(PICommunication.initialize_cameras())

    print("Starting main loop")
    while RUNNING:
        commands = gui_object.get_events()
        if commands:
            print(commands)
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
                pygame.quit()
                sys.exit()
                break
            else:
                server_tcp_stream.send_by_size(command.value)
        if not RUNNING:
            break
        time.sleep(1.0 / 24)
    LOCK.acquire()
    RUNNING = False
    LOCK.release()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
