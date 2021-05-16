import json
import socket
import threading
import time
from network.socket_utils import initialize_server
import cv2
from image_processing.image_utils import image_resize
from network.stream import Streamer

CAMERAS = {}
CONSTANTS_PATH = "constants.json"
DESTINATION_SIZE = (160, 120)
# DESTINATION_SIZE = (256, 192)
LOCK = threading.Lock()
STREAM_FRAME_SHAPE = (192, 256, 3)
STREAMERS = {}
THREADS = []


def handle_client(socket):
    while True:
        pass


def stream_video(streamer, camera):
    running = True
    while running:
        ret, frame = camera.read()
        if ret:
            resized_frame = image_resize(frame, DESTINATION_SIZE[1], DESTINATION_SIZE[0])
            streamer.send_image(resized_frame)
        time.sleep(1.0 / 24)


def initialize_streamers(left_address, right_address):
    global CAMERAS
    global STREAMERS
    left_udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    left_streamer = Streamer(left_udp_client_socket, left_address, 4, 4, 1024, 2)
    left_camera = cv2.VideoCapture(2)

    right_udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    right_streamer = Streamer(right_udp_client_socket, right_address, 4, 4, 1024, 2)
    right_camera = cv2.VideoCapture(4)

    LOCK.acquire()
    CAMERAS["left"] = left_camera
    STREAMERS["left"] = left_streamer

    CAMERAS["right"] = right_camera
    STREAMERS["right"] = right_streamer
    LOCK.release()


def main():
    global THREADS

    # constants = json.load(open(CONSTANTS_PATH))
    # tcp_server = initialize_server(constants)

    left_address = ("192.168.1.43", 10002)
    right_address = ("192.168.1.43", 10003)
    initialize_streamers(left_address, right_address)

    left_streaming_thread = threading.Thread(target=stream_video, args=(STREAMERS["left"], CAMERAS["left"]))
    right_streaming_thread = threading.Thread(target=stream_video, args=(STREAMERS["right"], CAMERAS["right"]))

    THREADS.append(left_streaming_thread)
    THREADS.append(right_streaming_thread)

    left_streaming_thread.start()
    right_streaming_thread.start()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
