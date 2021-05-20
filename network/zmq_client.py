import cv2
import imagezmq

imageHub = imagezmq.ImageHub()

while True:
    (camera_name, frame) = imageHub.recv_image()
    cv2.imshow("Received", frame)
    cv2.waitKey(1)
    imageHub.send_reply(b'OK')
