import socket

import cv2
import imagezmq

sender = imagezmq.ImageSender(connect_to="tcp://localhost:5555")
cap = cv2.VideoCapture(0)
cam_id = socket.gethostname()

while True:
    ret, frame = cap.read()
    if ret:
        sender.send_image(cam_id, frame)
