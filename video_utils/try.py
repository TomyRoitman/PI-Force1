import cv2
import time
cap1 = cv2.VideoCapture(2)
cap2 = cv2.VideoCapture(4)

while True:
	
	ret1, frame1 = cap1.read()
	if ret1:
		cv2.imshow("Cap1", frame1)
	
	ret2, frame2 = cap2.read()
	if ret2:
		cv2.imshow("Cap2", frame2)

	#time.sleep(1.0 / 25)

	if cv2.waitKey(1) & 0xFF == ord('q'):
    		break
