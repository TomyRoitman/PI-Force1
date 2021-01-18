import cv2
import imutils
from image_processing.calibration.camera_calibration_store import load_coefficients


class Camera(cv2.VideoCapture):

    def __init__(self, camera_id, calibration_file_path, rotate=False, angle=180):
        super().__init__(camera_id)
        self.camera_id = camera_id
        self.rotate = rotate
        self.angle = angle
        self.calibration_file_path = calibration_file_path
        self.__load_calibration()

    def __load_calibration(self):
        return load_coefficients(self.calibration_file_path)

    def read(self):
        ret, image = super().read()
        if ret and self.rotate:
            return ret, imutils.rotate(image, self.angle)
        return ret, image


def main():
    a = Camera(1, True)
    while True:
        ret, frame = a.read()
        if ret:
            cv2.imshow('a', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()