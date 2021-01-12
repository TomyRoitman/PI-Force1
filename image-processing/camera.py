import cv2
import imutils

class Camera(cv2.VideoCapture):

    def __init__(self, camera_id, flip=False, angle=180):
        super().__init__(camera_id)
        self.camera_id = camera_id
        self.flip = flip
        self.angle = angle


    def read(self):
        ret, image = super().read()
        if ret and self.flip:
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