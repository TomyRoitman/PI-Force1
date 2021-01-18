import cv2
import time
import sys
import imutils

# Set cameras ID's
left_camera = cv2.VideoCapture(1)
right_camera = cv2.VideoCapture(2)





def main():
    global i
    
    i = 0

    if len(sys.argv) < 4:
        print("Usage: ./program_name directory_to_save start_index prefix")
        return

    i = int(sys.argv[2])
    while True:

        # Capture frame-by-frame
        ret_left, left_frame = left_camera.read()
        ret_right, right_frame = right_camera.read()

        # Flip two frames
        left_frame = imutils.rotate(left_frame, 180)
        right_frame = imutils.rotate(right_frame, 180)

        # Display the resulting frame
        cv2.imshow('left_frame', left_frame)
        cv2.imshow('right_frame', right_frame)


        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('c'):
            cv2.imwrite(sys.argv[1] + "/" + sys.argv[3] + "_left" + str(i) + ".png", left_frame)
            cv2.imwrite(sys.argv[1] + "/" + sys.argv[3] + "_right" + str(i) + ".png", right_frame)
            i += 1

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()