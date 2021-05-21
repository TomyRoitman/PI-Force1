import pickle
import socket

import cv2
import math

MAX_LENGTH = 65000


class Streamer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(self.host, type(self.host), self.port, type(self.port))
        
    def send_frame(self, frame):

        # compress frame
        retval, buffer = cv2.imencode(".jpg", frame)

        if retval:
            # convert to byte array
            buffer = buffer.tobytes()
            # get size of the frame
            buffer_size = len(buffer)

            num_of_packs = 1
            if buffer_size > MAX_LENGTH:
                num_of_packs = math.ceil(buffer_size / MAX_LENGTH)

            frame_info = {"packs": num_of_packs}

            # send the number of packs to be expected
            # print("Number of packs:", num_of_packs)
            self.sock.sendto(pickle.dumps(frame_info), (self.host, self.port))

            left = 0
            right = MAX_LENGTH

            for i in range(num_of_packs):
                # print("left:", left)
                # print("right:", right)

                # truncate data to send
                data = buffer[left:right]
                left = right
                right += MAX_LENGTH

                # send the frames accordingly
                self.sock.sendto(data, (self.host, self.port))

import argparse
def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-a', '--address', dest='address',
                    help='<host>:<port> representing the destination address for the streamer')
    parser.add_argument('-i', '--video-device-id', dest='video_device_id',
                    help='Index of video device')

    args = parser.parse_args()
    print(args)

    address = args.address
    host, port = address.split(":")
    port = int(port)
    streamer = Streamer(host, port)
    id = int(args.video_device_id)
    cap = cv2.VideoCapture(id)
    print("Entering loop", host, port, args.video_device_id)
    while True:
        ret, frame = cap.read()

        if ret:
            streamer.send_frame(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    main()
