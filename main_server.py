import json
import threading
import time
from subprocess import Popen

import cv2

from car import Car
from image_processing.object_detection import ObjectDetector
from network.communication import TCPStream
# from network.communication import TCPServer
from network.protocol import PICommunication
from network.socket_utils import initialize_server
from network.streamer import Streamer

CAMERA_OPENED = {'left': False, 'right': False}
CAMERAS = {}
CAMERA_USED = {"left": False, "right": False}
CAMERA_INDEX = {"left": 0, "right": 2}
CONFIDENCE = 0.75
CONSTANTS_PATH = "constants.json"
# DESTINATION_SIZE = (160, 120)
DESTINATION_SIZE = (256, 192)
# DESTINATION_SIZE = (256, 192)
FPS = 24
GPIO_PIN_DISTRIBUTION_PATH = "gpio_pin_distribution.json"
LEFT_CAMERA_ADDRESS = "192.168.1.25:5000"
LEFT_CAMERA_INDEX = 0
LOCK = threading.Lock()
PROCESSES = []
RIGHT_CAMERA_ADDRESS = "192.168.1.25:5001"
CAMERA_ADDRESS = {"left": LEFT_CAMERA_ADDRESS, "right": RIGHT_CAMERA_ADDRESS}
RIGHT_CAMERA_INDEX = 2
RUNNING = True
# STREAM_FRAME_SHAPE = (192, 256, 3)
STREAMERS = {}
THREADS = []
PROCESSES = []



def main():
    global RUNNING
    global PROCESSES
    global THREADS
    global CAMERA_USEDc
    # detector = ObjectDetector("image_processing/", CONFIDENCE)

    constants = json.load(open(CONSTANTS_PATH))
    tcp_server = initialize_server(constants, "main_tcp_server", THREADS)
    client_socket = tcp_server.get_client()
    client_tcp_stream = TCPStream(client_socket, 1024, 4, 8, 1024)

    car = Car()
    while RUNNING:
        content_length, content = client_tcp_stream.recv_by_size()
        code, message = PICommunication.parse_message(content)

        try:
            # Car control:
            if code == PICommunication.MessageCode.MOVE_FORWARD:
                car.go_forward()
            elif code == PICommunication.MessageCode.MOVE_BACKWARDS:
                car.go_backwards()
            elif code == PICommunication.MessageCode.STOP:
                car.stop()
            elif code == PICommunication.MessageCode.LOW_SPEED:
                car.low()
            elif code == PICommunication.MessageCode.MEDIUM_SPEED:
                car.medium()
            elif code == PICommunication.MessageCode.HIGH_SPEED:
                car.high()
            elif code == PICommunication.MessageCode.TURN_RIGHT:
                car.turn_right()
            elif code == PICommunication.MessageCode.TURN_LEFT:
                car.turn_left()

            # Video stream control:
            elif code == PICommunication.MessageCode.INITIALIZE_CAMERAS:
                cameras = ["left", "right"]
                for camera in cameras:
                    if CAMERA_USED[camera]:
                        print("Camera already used!")
                    else:
                        print("Initializing stream for camera: ", camera)
                        id = CAMERA_INDEX[camera]
                        address = CAMERA_ADDRESS[camera]
                        print(id, address)
                        LOCK.acquire()
                        p = Popen(['python3', 'network/streamer.py', '-a', address, '-i', str(id)])
                        PROCESSES.append(p)
                        CAMERA_OPENED[camera] = True
                        LOCK.release()
            # General messages:
            elif code == PICommunication.MessageCode.DISCONNECT:
                client_tcp_stream.send_by_size(PICommunication.disconnect("User exited"))
                client_socket.close()
                break
            else:
                print(f"Command code: {code}\n")
                client_tcp_stream.send_by_size(PICommunication.error("Unknown command"))
        except Exception as e:
            print(e)

    LOCK.acquire()
    RUNNING = False
    LOCK.release()
    print("Processes: ", PROCESSES)
    for p in PROCESSES:
        print("Killing camera process with id: ", p.pid)
        p.kill()
    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
