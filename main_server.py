import socket
import threading
import time

import cv2

from network.stream import Streamer

STREAM_FRAME_SHAPE = (192, 256, 3)
# DESTINATION_SIZE = (256, 192)
DESTINATION_SIZE = (160, 120)


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (w, h) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (int(h * r), width)
    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized

def stream_video(left_streamer, left_camera, right_streamer, right_camera):
    running = True
    while running:
        left_ret, left_frame = left_camera.read()
        if left_ret:
            resized_left_frame = image_resize(left_frame, DESTINATION_SIZE[1], DESTINATION_SIZE[0])
            left_streamer.send_image(resized_left_frame)

        right_ret, right_frame = right_camera.read()
        if right_ret:
            resized_right_frame = image_resize(right_frame, DESTINATION_SIZE[1], DESTINATION_SIZE[0])
            right_streamer.send_image(resized_right_frame)

        time.sleep(1.0 / 24)


THREADS = []


def main():
    global THREADS

    left_address = ("192.168.1.43", 10002)
    left_address = ("localhost", 10002)
    left_udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    left_streamer = Streamer(left_udp_client_socket, left_address, 4, 4, 1024, 2)
    left_camera = cv2.VideoCapture(2)

    right_address = ("192.168.1.43", 10003)
    right_udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    right_streamer = Streamer(right_udp_client_socket, right_address, 4, 4, 1024, 2)
    right_camera = cv2.VideoCapture(4)
    # right_streamer = None
    # right_camera = None
    streaming_thread = threading.Thread(target=stream_video,
                                        args=(left_streamer, left_camera, right_streamer, right_camera))
    THREADS.append(streaming_thread)
    streaming_thread.start()

    for thread in THREADS:
        thread.join()


if __name__ == '__main__':
    main()


