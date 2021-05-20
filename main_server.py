import json
import socket
import threading
import time

import cv2

from car import Car
from image_processing.image_utils import image_resize
from image_processing.object_detection import ObjectDetector
from network.communication import TCPStream
# from network.communication import TCPServer
from network.protocol import PICommunication
from network.socket_utils import initialize_server
from network.stream import Streamer

CAMERA_CHOSEN = None
CAMERAS = {}
CONFIDENCE = 0.75
CONSTANTS_PATH = "constants.json"
# DESTINATION_SIZE = (160, 120)
DESTINATION_SIZE = (256, 192)
# DESTINATION_SIZE = (256, 192)
FPS = 24
GPIO_PIN_DISTRIBUTION_PATH = "gpio_pin_distribution.json"
LEFT_CAMERA_ADDRESS = ("192.168.1.43", 10002)
LEFT_CAMERA_INDEX = 0
LOCK = threading.Lock()
RIGHT_CAMERA_ADDRESS = ("192.168.1.43", 10003)
RIGHT_CAMERA_INDEX = 1
RUNNING = True
# STREAM_FRAME_SHAPE = (192, 256, 3)
STREAMERS = {}
THREADS = []


def initialize_streamer(camera):
    global CAMERAS
    global STREAMERS

    address = ()
    video_capture_device_index = -1
    if camera == "left":
        address = LEFT_CAMERA_ADDRESS
        video_capture_device_index = LEFT_CAMERA_INDEX
    elif camera == "right":
        address = RIGHT_CAMERA_ADDRESS
        video_capture_device_index = RIGHT_CAMERA_INDEX
    else:
        return None

    udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    streamer = Streamer(udp_client_socket, address, 4, 4, 1024, 2)
    camera = cv2.VideoCapture(video_capture_device_index)

    return streamer, camera


def stream_video(detector: ObjectDetector):
    camera = None
    old_camera_chosen = None
    streamer = None
    # print("Streaming video!")
    while RUNNING:

        if CAMERA_CHOSEN != old_camera_chosen:
            stream_utils = initialize_streamer(CAMERA_CHOSEN)
            if not stream_utils:
                continue
            streamer, camera = stream_utils
            old_camera_chosen = CAMERA_CHOSEN

        # Show frames:
        if streamer and camera:
            ret, frame = camera.read()
            if ret:
                results = detector.detect(frame)
                print(results)
                resized_frame = image_resize(frame, DESTINATION_SIZE[1], DESTINATION_SIZE[0])
                streamer.send_image(resized_frame)
        time.sleep(1.0 / FPS)

    cv2.destroyAllWindows()


def main():
    global CAMERA_CHOSEN
    global RUNNING
    global THREADS
    detector = ObjectDetector("image_processing/", CONFIDENCE)
    stream_video_thread = threading.Thread(target=stream_video, args=(detector,))
    THREADS.append(stream_video_thread)
    stream_video_thread.start()

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
            elif code == PICommunication.MessageCode.CHOOSE_CAMERA:
                LOCK.acquire()
                CAMERA_CHOSEN = message
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

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
