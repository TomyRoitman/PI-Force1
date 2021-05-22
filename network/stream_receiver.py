import pickle
import socket
import threading

import cv2
import numpy as np

MAX_LENGTH = 65540


class StreamReceiver:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.frame_queue = []
        self.running = True

    def receive_stream(self):
        frame_info = None
        buffer = None
        frame = None

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        print("-> waiting for connection", self.host, self.port)
        while self.running:
            data, address = sock.recvfrom(MAX_LENGTH)

            if len(data) < 100:
                frame_info = pickle.loads(data)

                if frame_info:
                    nums_of_packs = frame_info["packs"]

                    for i in range(nums_of_packs):
                        data, address = sock.recvfrom(MAX_LENGTH)

                        if i == 0:
                            buffer = data
                        else:
                            buffer += data

                    frame = np.frombuffer(buffer, dtype=np.uint8)
                    frame = frame.reshape(frame.shape[0], 1)

                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    frame = cv2.flip(frame, 1)

                    if frame is not None and type(frame) == np.ndarray:
                        self.lock.acquire()
                        self.frame_queue.append(frame)
                        self.lock.release()


def main():
    receiver1 = StreamReceiver('0.0.0.0', 5000)
    t1 = threading.Thread(target=receiver1.receive_stream)
    t1.start()

    receiver2 = StreamReceiver('0.0.0.0', 5001)
    t2 = threading.Thread(target=receiver2.receive_stream)
    t2.start()
    left_frame = None
    right_frame = None
    i = 0
    while True:
        if receiver1.frame_queue:
            left_frame = receiver1.frame_queue.pop(0)
            cv2.imshow("Receiver1", left_frame)

        if receiver2.frame_queue:
            right_frame = receiver2.frame_queue.pop(0)
            cv2.imshow("Receiver2", right_frame)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            receiver1.running = False
            receiver2.running = False
            break
        elif key == ord('c'):
            print("Saving picture", i)
            cv2.imwrite("../image_processing/calibration/images/cal_left" + str(i) + ".jpg", left_frame)
            cv2.imwrite("../image_processing/calibration/images/cal_right" + str(i) + ".jpg", right_frame)
            i += 1

if __name__ == '__main__':
    main()
