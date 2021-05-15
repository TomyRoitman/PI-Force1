import socket
import threading

import cv2

from network.stream import Streamer


def stream_video(left_streamer, left_camera, right_streamer, right_camera):
    pass


THREADS = []

if __name__ == '__main__':
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
