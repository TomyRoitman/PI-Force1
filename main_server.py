import json
import socket
import threading
import time
from multiprocessing import Process
import cv2
from subprocess import Popen
from car import Car
from image_processing.image_utils import image_resize
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
LEFT_CAMERA_ADDRESS = "192.168.1.43:5000"
LEFT_CAMERA_INDEX = 0
LOCK = threading.Lock()
PROCESSES = []
RIGHT_CAMERA_ADDRESS = "192.168.1.43:5001"
CAMERA_ADDRESS = {"left": LEFT_CAMERA_ADDRESS, "right":RIGHT_CAMERA_ADDRESS}
RIGHT_CAMERA_INDEX = 2
RUNNING = True
# STREAM_FRAME_SHAPE = (192, 256, 3)
STREAMERS = {}
THREADS = []


def stream_video(host: str, port: int, camera_index: int, detector: ObjectDetector):
    streamer = Streamer(host, port)
    camera = cv2.VideoCapture(camera_index)
    while RUNNING:

        ret, frame = camera.read()
        if ret:
            # results = detector.detect(frame)
            # print(results)
            streamer.send_frame(frame)
        time.sleep(1.0 / FPS)

    cv2.destroyAllWindows()


def main():
    global CAMERA_CHOSEN
    global RUNNING
    global PROCESSES
    global THREADS
    #detector = ObjectDetector("image_processing/", CONFIDENCE)

    #stream_video_process1 = Process(target=stream_video, args=('192.168.1.43', 5000, 0, detector))
    # THREADS.append(stream_video_thread1)
    #PROCESSES.append(stream_video_process1)
   # stream_video_process1.start()

  #  stream_video_process2 = Process(target=stream_video, args=('192.168.1.43', 5001, 2, detector))
 #   PROCESSES.append(stream_video_process2)
    # THREADS.append(stream_video_thread2)
#    stream_video_process2.start()

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
                camera = message
                if not CAMERA_USED[camera]:
                    print("Initializing stream for camera: ", camera)
                    id = CAMERA_INDEX[camera]
                    address = CAMERA_ADDRESS[camera]
                    print(id, address)
                    l = ['python3', 'network/streamer.py', '-a', address, '-i', str(id)]
                    print(l)
                    Popen(l)
                    LOCK.acquire()
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

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()
