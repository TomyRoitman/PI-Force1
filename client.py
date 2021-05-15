from network.stream import Streamer
import cv2
import socket
import time
udp_client_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

streamer = Streamer(udp_client_sock, ("127.0.0.1", 10003), 4, 4, 1024, 2)

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    # resized_frame = cv2.resize(frame, (256, 192))
    resized_frame = cv2.resize(frame, (320, 240))
    streamer.send_image(resized_frame)
    # Display the resulting frame
    cv2.imshow('Streamer', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1.0 / 60)
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
