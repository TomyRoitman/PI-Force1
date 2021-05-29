import json
import socket
import sys
import threading
import time

import cv2
import imagehash
import numpy as np
import pygame
from PIL import Image

from gui import Gui, Commands
from image_processing.distance import DistanceCalculator2
from image_processing.object_detection import ObjectDetector, DetectionResult
from image_processing.stereo import StereoDepthMap
from network.communication import TCPStream
from network.protocol import PICommunication
from network.stream_receiver import StreamReceiver
from try_distance import DistanceCalculator3

CUTOFF = 50
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
        if len(FRAME_QUEUE) > 2:
            LOCK.acquire()
            not_used = FRAME_QUEUE.pop(0)
            not_used2 = FRAME_QUEUE.pop(0)
            left_frame, right_frame = FRAME_QUEUE.pop(0)
            ret = True
            LOCK.release()
        if ret:
            depth_map = depth_map_obj.get_depth_image(left_frame, right_frame)
            DEPTH_MAP_QUEUE.append(depth_map)
        # cv2.waitKey(1)
        time.sleep(1.0 / 60)
    sys.exit()


def blit_frame(screen, frame, size, position):
    frame_blit = cv2.resize(frame, size)
    frame_blit = cv2.flip(frame_blit, 1)  # flip horizontal
    frame_blit = cv2.cvtColor(frame_blit, cv2.COLOR_BGR2RGB)
    frame_blit = np.rot90(frame_blit)
    surface = pygame.surfarray.make_surface(frame_blit)
    if RUNNING:
        screen.blit(surface, position)


def compare_images(frame0, frame1):
    try:
        im0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2RGB)
        im0 = Image.fromarray(im0)
        hash0 = imagehash.average_hash(im0)
        im1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        im1 = Image.fromarray(im1)
        hash1 = imagehash.average_hash(im1)
        to_return = (hash0 - hash1) < CUTOFF
        return to_return
    except:
        return False


def get_object_from_detection_result(frame: np.ndarray, detection_result: DetectionResult):
    return frame[detection_result.location[1]:detection_result.location[3],
           detection_result.location[0]:detection_result.location[2]]


def find_object_pairs(left_frame, left_results, right_frame, right_results, distance_calculator: DistanceCalculator2):
    left_results.sort(key=lambda obj: obj.obj_type)
    right_results.sort(key=lambda obj: obj.obj_type)
    # right_obj_types = [result.obj_type for result in right_results]
    right_index = 0
    for left_obj in left_results:
        for right_obj in right_results:
            if left_obj.obj_type != right_obj.obj_type:
                right_index = right_results.index(right_obj)
                break
            try:
                left_cropped_obj = get_object_from_detection_result(left_frame, left_obj)
                right_cropped_obj = get_object_from_detection_result(right_frame, right_obj)

                if compare_images(left_cropped_obj, right_cropped_obj):
                    # l_x = (left_obj.location[0] + left_obj.location[2]) / 2.0
                    # l_y = (left_obj.location[1] + left_obj.location[3]) / 2.0
                    # r_x = (right_obj.location[0] + right_obj.location[2]) / 2.0
                    # r_y = (right_obj.location[1] + right_obj.location[3]) / 2.0
                    # # print("x1m, y1m, x2m, y2m", l_x, ",", l_y, ",", r_x, ",", r_y)
                    # print(l_x, r_x)
                    # distance = distance_calculator.calculate_distance(l_x, l_y, r_x, r_y)
                    X, Y, Z, D = distance_calculator.calculate_distance(
                        (left_obj.location[0] + left_obj.location[2]) / 2.0,
                        (left_obj.location[1] + left_obj.location[3]) / 2.0,
                        (right_obj.location[0] + right_obj.location[2]) / 2.0,
                        (right_obj.location[1] + right_obj.location[3]) / 2.0)
                    # print(f"Distance from {left_obj.obj_type}: {X}, {Y}, {Z}, {D}")
                    distance_string = f" X: {X}, Y: {Y}, Z: {Z}, D: {D}"
                    left_obj.label += distance_string
                    right_obj.label += distance_string
                    break
            except Exception as e:
                print(e)
            right_results = right_results[right_index:]


def put_results_on_frame(frame, results):
    for result in results:
        (startX, startY, endX, endY) = result.location
        cv2.rectangle(frame, (startX, startY), (endX, endY), result.color, 2)
        # y = startY + 15 if startY + 15 < 640 else startY + 15
        i = 2
        for field in result.label.split(", "):
            cv2.putText(frame, field, (startX + 15, startY + i * 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, result.color, 2)
            i += 1

def handle_stream(constants, screen):
    global THREADS

    depth_map_thread = threading.Thread(target=create_depth_map)
    depth_map_thread.start()
    LOCK.acquire()
    THREADS.append(depth_map_thread)
    LOCK.release()
    distance_calculator = DistanceCalculator3()
    # distance_calculator = DistanceCalculator()
    receiver1, receiver2 = initialize_receivers(constants)
    detector = ObjectDetector("image_processing/", CONFIDENCE)
    left_results = []
    right_results = []
    # screen.fill(BACKGROUND_COLOR)
    left_frame = None
    right_frame = None
    running = RUNNING
    while running:

        LOCK.acquire()

        # Get left frame
        if receiver1.frame_queue:
            left_ret = True
            # LOCK.acquire()
            left_frame = receiver1.frame_queue.pop(0)
            # LOCK.release()
            frame, left_results = detector.detect(left_frame)

        else:
            left_ret = False

        # Get right frame
        if receiver2.frame_queue:
            right_ret = True
            # LOCK.acquire()
            right_frame = receiver2.frame_queue.pop(0)
            # LOCK.release()
            frame, right_results = detector.detect(right_frame)

        else:
            right_ret = False

        # Handle stereo cases
        if left_ret and right_ret:

            # Create depth map
            # LOCK.acquire()
            FRAME_QUEUE.append((left_frame, right_frame))
            if DEPTH_MAP_QUEUE:
                if RUNNING:
                    depth_map = DEPTH_MAP_QUEUE.pop(0)
                    depth_map_size = (300, 225)
                    blit_frame(screen, depth_map, depth_map_size, ((SCREEN_DIMENSIONS[0] - depth_map_size[0]) / 2, 550))
                else:
                    break
            # LOCK.release()

            # Handle object detection and distance measurement
            find_object_pairs(left_frame, left_results, right_frame, right_results,
                              distance_calculator)  # Calculate distance from objects

        LOCK.release()

        if left_frame is not None:
            if left_results:
                put_results_on_frame(left_frame, left_results)
            left_frame_size = (640, 480)
            blit_frame(screen, left_frame, left_frame_size, (SCREEN_DIMENSIONS[0] / 2, 50))
        if right_frame is not None:
            if right_results:
                put_results_on_frame(right_frame, right_results)
            right_frame_size = (640, 480)
            blit_frame(screen, right_frame, right_frame_size, (SCREEN_DIMENSIONS[0] / 2 - right_frame_size[0], 50))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.JOYBUTTONDOWN and event.button == 7):
                pygame.quit()
                sys.exit()

    pygame.quit()
    sys.exit()


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

    server_tcp_stream = TCPStream(server_socket, 1024, 4, 8, 1024, False)

    print("[Log] Sending: Request for camera initialization")
    server_tcp_stream.send_by_size(PICommunication.initialize_cameras())

    print("Starting main loop")
    while RUNNING:
        commands = gui_object.get_events()
        # if commands:
        # print(commands)
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
        time.sleep(1.0 / 50)
    LOCK.acquire()
    RUNNING = False
    LOCK.release()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
