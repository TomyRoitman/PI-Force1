from network.stream import Streamer
import cv2
import socket
import time
udp_client_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

<<<<<<< HEAD
streamer = Streamer(udp_client_sock, ("127.0.0.1", 10003), 2, 2, 1024, 2)
=======
streamer = Streamer(udp_client_sock, ("127.0.0.1", 10002), 25, 1024, 2)
>>>>>>> 1c7e733fee9c1f443291c8f965341d8f58ec4b54

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    streamer.send_image(frame)
    # Display the resulting frame
    cv2.imshow('Streamer', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1.0 / 15)
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
