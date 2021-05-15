import json
import threading
import time

import cv2

from network.server import TCPServer, UDPServer
from network.stream import StreamReceiver

CONSTANTS_PATH = "constants.json"
DESTINATION_SIZE = (480, 640)
STREAM_FRAME_SHAPE = (192, 256, 3)
STREAM_FRAME_GRID_ROWS = 4
STREAM_FRAME_GRID_COLUMNS = 4
THREADS = []


def handle_client(socket):
    while True:
        pass


def initialize_server(constants, server_name, new_thread=True):
    global THREADS
    server_info = constants[server_name]
    if server_info["type"] == "tcp":
        server = TCPServer((server_info["ip"], int(server_info["port"])), server_info["recv_size"], handle_client)
    elif server_info["type"] == "udp":
        server = UDPServer((server_info["ip"], int(server_info["port"])), server_info["recv_size"])
    else:
        raise ValueError(f"Invalid server_type: {server_name}")

    if new_thread:
        server_thread = threading.Thread(target=server.run, args=())
        THREADS.append(server_thread)
        server_thread.start()
    else:
        server.run()

    return server


def main():
    global THREADS
    constants = json.load(open(CONSTANTS_PATH))

    left_camera_udp_server = initialize_server(constants, "udp_server_left_camera")
    left_stream_receiver = StreamReceiver(left_camera_udp_server, STREAM_FRAME_SHAPE, True, STREAM_FRAME_GRID_ROWS,
                                          STREAM_FRAME_GRID_COLUMNS, left_camera_udp_server.recv_size)

    right_camera_udp_server = initialize_server(constants, "udp_server_right_camera")
    right_stream_receiver = StreamReceiver(right_camera_udp_server, STREAM_FRAME_SHAPE, True, STREAM_FRAME_GRID_ROWS,
                                           STREAM_FRAME_GRID_COLUMNS, left_camera_udp_server.recv_size)

    running = True
    while running:
        left_frame = left_stream_receiver.get_frame()
        resized_left_frame = cv2.resize(left_frame, DESTINATION_SIZE)
        cv2.imshow("Left Camera", resized_left_frame)

        right_frame = right_stream_receiver.get_frame()
        resized_right_frame = cv2.resize(right_frame, DESTINATION_SIZE)
        cv2.imshow("Right Camera", resized_right_frame)

        time.sleep(1.0 / 60)


if __name__ == '__main__':
    main()
