import socket
import threading
import time

import cv2

from network.stream import Streamer

STREAM_FRAME_SHAPE = (192, 256, 3)
DESTINATION_SIZE = (480, 640)


def stream_video(left_streamer, left_camera, right_streamer, right_camera):
    running = True
    while running:
        left_ret, left_frame = left_camera.read()
        if left_ret:
            resized_left_frame = cv2.resize(left_frame, DESTINATION_SIZE)
            left_streamer.send_image(resized_left_frame)

        right_ret, right_frame = right_camera.read()
        if right_ret:
            resized_right_frame = cv2.resize(right_frame, DESTINATION_SIZE)
            right_streamer.send_image(resized_right_frame)

        time.sleep(1.0 / 60)


THREADS = []


def main():
    global THREADS

    left_address = ("192.168.1.43", 10002)
    left_udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    left_streamer = Streamer(left_udp_client_socket, left_address, 4, 4, 1024, 2)
    left_camera = cv2.VideoCapture(0)

    right_address = ("192.168.1.43", 10003)
    right_udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    right_streamer = Streamer(right_udp_client_socket, right_address, 4, 4, 1024, 2)
    right_camera = cv2.VideoCapture(1)

    streaming_thread = threading.Thread(target=stream_video,
                                        args=(left_streamer, left_camera, right_streamer, right_camera))
    THREADS.append(streaming_thread)
    streaming_thread.start()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
