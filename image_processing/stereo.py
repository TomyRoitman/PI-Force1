import cv2
import numpy as np

from image_processing.calibration.camera_calibration_store import load_stereo_coefficients


class StereoDepthMap:
    def __init__(self, stereo_calibration_file):
        self.stereo_calibration_file = stereo_calibration_file
        print("Loading stereo calibration")
        self.__load_stereo_calibration()
        print("Finished loading stereo calibration")

    def __load_stereo_calibration(self):
        self.K1, self.D1, self.K2, self.D2, self.R, self.T, self.E, self.F, self.R1, self.R2, self.P1, self.P2, self.Q = load_stereo_coefficients(self.stereo_calibration_file)  # Get cams params
        
    def get_depth_image(self, left_frame, right_frame):
        height, width, channel = left_frame.shape  # We will use the shape for remap
        print(f"height {height}, width {width}, channel {channel}")
        # Undistortion and Rectification part!
        leftMapX, leftMapY = cv2.initUndistortRectifyMap(self.K1, self.D1, self.R1, self.P1, (width, height), cv2.CV_32FC1)
        left_rectified = cv2.remap(left_frame, leftMapX, leftMapY, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
        rightMapX, rightMapY = cv2.initUndistortRectifyMap(self.K2, self.D2, self.R2, self.P2, (width, height), cv2.CV_32FC1)
        right_rectified = cv2.remap(right_frame, rightMapX, rightMapY, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
         # We need grayscale for disparity map.
        gray_left = cv2.cvtColor(left_rectified, cv2.COLOR_BGR2GRAY)
        gray_right = cv2.cvtColor(right_rectified, cv2.COLOR_BGR2GRAY)
        disparity_image = self.__create_depth_map(gray_left, gray_right)  # Get the disparity map
        return disparity_image


    def __create_depth_map(self, imgL, imgR):
        """ Depth map calculation. Works with SGBM and WLS. Need rectified images, returns depth map ( left to right disparity ) """
        # SGBM Parameters -----------------
        window_size = 5  # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely

        left_matcher = cv2.StereoSGBM_create(
            minDisparity=-1,
            numDisparities=5*16,  # max_disp has to be dividable by 16 f. E. HH 192, 256
            blockSize=window_size,
            P1=8 * 3 * window_size,
            # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
            P2=32 * 3 * window_size,
            disp12MaxDiff=12,
            uniquenessRatio=10,
            speckleWindowSize=50,
            speckleRange=32,
            preFilterCap=63,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
        )
        right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
        # FILTER Parameters
        lmbda = 80000
        sigma = 1.3
        visual_multiplier = 6

        wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=left_matcher)
        wls_filter.setLambda(lmbda)

        wls_filter.setSigmaColor(sigma)
        displ = left_matcher.compute(imgL, imgR)  # .astype(np.float32)/16
        dispr = right_matcher.compute(imgR, imgL)  # .astype(np.float32)/16
        displ = np.int16(displ)
        dispr = np.int16(dispr)
        filteredImg = wls_filter.filter(displ, imgL, None, dispr)  # important to put "imgL" here!!!

        # filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX);
        filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=255, alpha=0, norm_type=cv2.NORM_MINMAX);
        filteredImg = np.uint8(filteredImg)

        return filteredImg


