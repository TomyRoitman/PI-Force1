import numpy as np
import cv2
import glob
import argparse
from camera_calibration_store import save_coefficients

# source: https://aliyasineser.medium.com/opencv-camera-calibration-e9a48bdd1844
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def calibrate(dirpath: str, prefix: str, image_format: str, square_size: float, width=9, height=6):
    """
    Operation
    ----------

    Apply camera calibration operation for images in the given directory path
    prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)

    Parameters
    ----------
    
    dirpath: str
        The directory that we moved our images.
    
    prefix: str
        Images should have the same name. This prefix represents that name. (If the list is: image1.jpg, image2.jpg … it shows that the prefix is “image”.
        Code is generalized but we need a prefix to iterate, otherwise, there can be any other file that we don’t care about.)
    
    image_format: str
        “jpg” or“png”. These formats are supported by OpenCV.
    
    square_size: float
        Edge size of one square.
    
    width: int
        Number of intersection points of squares in the long side of the calibration board. It is 9 by default if you use the chessboard above.
    
    height: int 
        Number of intersection points of squares in the short side of the calibration board. It is 6by default if you use the chessboard above.
    """

    objp = np.zeros((height*width, 3), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)

    objp = objp * square_size # if square_size is 1.5 centimeters, it would be better to write it as 0.015 meters. 
    # Meter is a better metric because most of the time we are working on meter level projects.

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    # Some people will add "/" character to the end. It may brake the code so I wrote a check.
    if dirpath[-1:] == '/':
        dirpath = dirpath[:-1]
    images = glob.glob(dirpath+'/' + prefix + '*.' + image_format) #
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (width, height), None)
        print(fname, ret, type(corners), "\n")
        # If found, add object points, image points (after refining them)
        if ret:
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            print(type(objp), type(corners2), "\n\n")

            objpoints.append(objp)
            imgpoints.append(corners2)
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (width, height), corners2, ret)
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    return [ret, mtx, dist, rvecs, tvecs]


def main():

    # Check the help parameters to understand arguments
    parser = argparse.ArgumentParser(description='Camera calibration')
    parser.add_argument('--image_dir', type=str, required=True, help='image directory path')
    parser.add_argument('--image_format', type=str, required=True,  help='image format, png/jpg')
    parser.add_argument('--prefix', type=str, required=True, help='image prefix')
    parser.add_argument('--square_size', type=float, required=False, help='chessboard square size')
    parser.add_argument('--width', type=int, required=False, help='chessboard width size, default is 9')
    parser.add_argument('--height', type=int, required=False, help='chessboard height size, default is 6')
    parser.add_argument('--save_file', type=str, required=True, help='YML file to save calibration matrices')

    args = parser.parse_args()

    # Call the calibraton and save as file. RMS is the error rate, it is better if rms is less than 0.2
    ret, mtx, dist, rvecs, tvecs = calibrate(args.image_dir, args.prefix, args.image_format, args.square_size, args.width, args.height)
    save_coefficients(mtx, dist, args.save_file)
    print("Calibration is finished. RMS: ", ret)

if __name__ == "__main__":
    main()