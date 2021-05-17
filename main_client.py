import json
import socket
import threading
import time
from enum import Enum

from image_processing.image_utils import image_resize
from network.communication import TCPStream
from network.protocol import PICommunication
from network.socket_utils import initialize_server
import cv2

from network.stream import StreamReceiver

CAMERA_CHOSEN = None
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
CONSTANTS_PATH = "constants.json"
DESTINATION_SIZE = (640, 480)
FPS = 24
LOCK = threading.Lock()
MAIN_TCP_SERVER_ADDRESS = ("0.0.0.0", 10001)
MAIN_MENU_TEXT = """
[1] Control car movement\n
[2] Choose stream source\n
[3] Exit\n"""
# STREAM_FRAME_SHAPE = (192, 256, 3)
STREAM_FRAME_SHAPE = (192, 256, 3)
STREAM_FRAME_GRID_ROWS = 4
STREAM_FRAME_GRID_COLUMNS = 4
# RECEIVERS = {}
RUNNING = True
THREADS = []


def initialize_receiver(constants, receiver):
    server_name = ""
    if receiver == "left":
        server_name = "udp_server_left_camera"
    elif receiver == "right":
        server_name = "udp_server_right_camera"
    else:
        return None
    print(f"[Log] - initializing camera_udp_server for camera: {server_name}")
    camera_udp_server = initialize_server(constants, server_name, THREADS)
    print(f"[Log] Created camera_udp_server: {camera_udp_server}")
    stream_receiver = StreamReceiver(camera_udp_server, STREAM_FRAME_SHAPE, True, STREAM_FRAME_GRID_ROWS,
                                     STREAM_FRAME_GRID_COLUMNS, camera_udp_server.recv_size)
    stream_receiver_thread = threading.Thread(target=stream_receiver.receive_stream)
    THREADS.append(stream_receiver_thread)
    stream_receiver_thread.start()

    return stream_receiver


def show_stream(constants):
    old_camera_chosen = None
    stream_receiver = None
    i = 0
    # start_time = time.time()
    while RUNNING:
        # i += 1
        # if (time.time() - start_time) != 0 and CAMERA_CHOSEN:
        # print(f"[Log] - FPS: {i / float(time.time() - start_time)}")
        # print("[Log] showing stream")
        if CAMERA_CHOSEN != old_camera_chosen:
            stream_receiver = initialize_receiver(constants, CAMERA_CHOSEN)
            old_camera_chosen = CAMERA_CHOSEN

        # Show frames:
        if not stream_receiver:
            continue
        # print(f"[Log] - Initialized stream receiver")
        frame = stream_receiver.get_frame()
        # print(f"[Log] got frame of shape: {frame.shape}")
        if frame is not None:
            # resized_frame = image_resize(frame, DESTINATION_SIZE[0], DESTINATION_SIZE[1])
            resized_frame = cv2.resize(frame, DESTINATION_SIZE)
            cv2.imshow(f"Stream from camera", resized_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # time.sleep(1.0 / FPS)


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
            duration = input("Insert movement duration in seconds:\n")
            while not isfloat(duration):
                duration = input("Could not convert time to float. Please insert again:\n")
            message = PICommunication.turn_right(float(duration))
        elif command == "tl":
            duration = input("Insert movement length in seconds:\n")
            while not isfloat(duration):
                duration = input("Could not convert time to float. Please insert again:\n")
            message = PICommunication.turn_left(float(duration))
        elif command == "q":
            break
        else:
            print(f"Command unknown: {command}\n")
            continue
        if message:
            server_tcp_stream.send_by_size(message)


def handle_stream_source_menu(server_tcp_stream: TCPStream):
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
    global CAMERA_CHOSEN
    global RUNNING
    global THREADS
    constants = json.load(open(CONSTANTS_PATH))
    show_stream_thread = threading.Thread(target=show_stream, args=(constants,))
    THREADS.append(show_stream_thread)
    show_stream_thread.start()

    server_socket = socket.socket()
    server_tcp_stream = TCPStream(server_socket, 1024, 4, 8, 1024)
    try:
        server_socket.connect(MAIN_TCP_SERVER_ADDRESS)
    except socket.error as e:
        raise socket.error("Could not connect to server. Failed with error:\n" + str(e))

    # camera_choice = input("Please choose a camera to be displayed:\n" + CAMERA_MENU_TEXT)
    # while not camera_choice.isdigit() or not 1 <= int(camera_choice) <= 3:
    #     camera_choice = input(
    #         "Invalid input. Please choose one of the following options:\n" + CAMERA_MENU_TEXT)
    # LOCK.acquire()
    # CAMERA_CHOSEN = StreamOptions(int(camera_choice)).name if camera_choice != "none" else None
    # print(CAMERA_CHOSEN)
    # LOCK.release()
    #
    # server_tcp_stream.send_by_size(PICommunication.choose_camera(CAMERA_CHOSEN))

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
