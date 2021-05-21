import json
import socket
import threading
from enum import Enum

import cv2
from network.stream_receiver import StreamReceiver

from network.communication import TCPStream
from network.protocol import PICommunication

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
MAIN_TCP_SERVER_ADDRESS = ("192.168.1.47", 10001)
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


def show_stream(constants):
    receiver1, receiver2 = initialize_receivers(constants)

    while RUNNING:

        if receiver1.frame_queue:
            frame = receiver1.frame_queue.pop(0)
            cv2.imshow("Receiver1", frame)

        if receiver2.frame_queue:
            frame = receiver2.frame_queue.pop(0)
            cv2.imshow("Receiver2", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


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
            LOCK.acquire()
            CAMERA_CHOSEN = StreamOptions(int(command)).name
            LOCK.release()
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
    try:
        server_socket.connect(MAIN_TCP_SERVER_ADDRESS)
    except socket.error as e:
        raise socket.error("Could not connect to server. Failed with error:\n" + str(e))
    server_tcp_stream = TCPStream(server_socket, 1024, 4, 8, 1024)

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
