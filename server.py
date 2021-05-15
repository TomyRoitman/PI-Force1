import json
import threading

from network.server import TCPServer, UDPServer
from network.stream import StreamReceiver

import time
import cv2
# import gobject
# gobject.threads_init()
# from car import Car

CONSTANTS_PATH = "constants.json"
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
        print("here")
        server_thread = threading.Thread(target=server.run, args=())
        print("here")
        THREADS.append(server_thread)
        print("here")
        server_thread.start()
        print("after")
    else:
        print("there")
        server.run()

    return server


def main():
    global THREADS    
    constants = json.load(open(CONSTANTS_PATH))

    # car = Car()
    # initialize_server(constants, "main_tcp_server")
    udp_server = initialize_server(constants, "main_udp_server")



    stream_receiver = StreamReceiver(udp_server, (192, 256, 3), True, 4, 4, 1024)
    # stream_receiver = StreamReceiver(udp_server, (240, 320, 3), True, 4, 4, 1024)
    # stream_receiver = StreamReceiver(udp_server, (480, 640, 3), True, 4, 4, 1024)
    stream_receiver_thread = threading.Thread(target=stream_receiver.receive_stream, args=())
    THREADS.append(stream_receiver_thread)
    stream_receiver_thread.start()
    while True:
        frame = stream_receiver.get_frame()
        resized_frame = cv2.resize(frame, (640, 480))
        cv2.imshow("StreamReceiver", resized_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1.0 / 60)
    # When everything done, release the capture
    cv2.destroyAllWindows()
    stream_receiver.running = False

if __name__ == '__main__':
    main()
