import time

import cv2

from image_processing.camera import Camera
from image_processing.stereo import StereoDepthMap


def main():
    left_camera = Camera(1, "image_processing/calibration/left_cam.yml", True)
    right_camera = Camera(2, "image_processing/calibration/right_cam.yml", True)

    depth_map_obj = StereoDepthMap("image_processing/calibration/stereo_cam.yml")
    print(depth_map_obj.__dict__)
    while True:
    # for i in range(1):


        ret_left, left_frame = left_camera.read()
        if ret_left:
            cv2.imshow("left_frame", left_frame)
        print("Opened left camera")
        
        ret_right, right_frame = right_camera.read()
        if ret_right:
            cv2.imshow("right_frame", right_frame)

        print("Opened right camera")

        if ret_left and ret_right:
            print("Starting to create depth map")

            depth_map = depth_map_obj.get_depth_image(left_frame, right_frame)
            print("Finished creating depth map")

            backtorgb = cv2.applyColorMap(depth_map, cv2.COLORMAP_SPRING)
            cv2.imshow("disparity", depth_map)
            cv2.imshow("colored disparity", backtorgb)
            # cv2.imwrite("map.png", depth_map)
        

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Get key to stop stream. Press q for exit
            break

        time.sleep(1.0 / 25)
if __name__ == "__main__":
    main()