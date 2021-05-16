import json
import threading
import time
from network.socket_utils import initialize_server
import cv2

from network.stream import StreamReceiver

CONSTANTS_PATH = "constants.json"
DESTINATION_SIZE = (640, 480)
LOCK = threading.Lock()
# STREAM_FRAME_SHAPE = (192, 256, 3)
STREAM_FRAME_SHAPE = (120, 160, 3)
STREAM_FRAME_GRID_ROWS = 4
STREAM_FRAME_GRID_COLUMNS = 4
RECEIVERS = {}
THREADS = []


def initialize_receivers(constants):
    global RECEIVERS
    left_camera_udp_server = initialize_server(constants, "udp_server_left_camera", THREADS)
    left_stream_receiver = StreamReceiver(left_camera_udp_server, STREAM_FRAME_SHAPE, True, False,
                                          STREAM_FRAME_GRID_ROWS, STREAM_FRAME_GRID_COLUMNS,
                                          left_camera_udp_server.recv_size)
    left_stream_receiver_thread = threading.Thread(target=left_stream_receiver.receive_stream, args=())
    THREADS.append(left_stream_receiver_thread)
    left_stream_receiver_thread.start()

    right_camera_udp_server = initialize_server(constants, "udp_server_right_camera", THREADS)
    right_stream_receiver = StreamReceiver(right_camera_udp_server, STREAM_FRAME_SHAPE, True, False,
                                           STREAM_FRAME_GRID_ROWS, STREAM_FRAME_GRID_COLUMNS,
                                           left_camera_udp_server.recv_size)
    right_stream_receiver_thread = threading.Thread(target=right_stream_receiver.receive_stream, args=())
    THREADS.append(right_stream_receiver_thread)
    right_stream_receiver_thread.start()

    LOCK.acquire()
    RECEIVERS["left"] = left_stream_receiver
    RECEIVERS["right"] = right_stream_receiver
    LOCK.release()




def main():
    global THREADS
    constants = json.load(open(CONSTANTS_PATH))
    initialize_receivers(constants)

    # streamer_choice = input("Please choose camera to display:\n[1] Left Camera\n[2] Right Camera\n[3] None\n")
    # while not streamer_choice.isdigit() or not 1 <= int(streamer_choice) <= 3:
    #     streamer_choice = input(
    #         "Invalid input. Please choose one of the following:\n[1] Left Camera\n[2] Right Camera\n[3] None\n")
    # streamer_choice = int(streamer_choice)

    left_stream_receiver = RECEIVERS["left"]
    right_stream_receiver = RECEIVERS["right"]

    running = True
    while running:
        left_frame = left_stream_receiver.get_frame()
        if left_frame is not None:
            resized_left_frame = cv2.resize(left_frame, DESTINATION_SIZE)
            cv2.imshow("Left Camera", resized_left_frame)

        right_frame = right_stream_receiver.get_frame()
        if right_frame is not None:
            resized_right_frame = cv2.resize(right_frame, DESTINATION_SIZE)
            cv2.imshow("Right Camera", resized_right_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(1.0 / 24)


if __name__ == '__main__':
    main()
