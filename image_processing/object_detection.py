import cv2
import numpy as np


class DetectionResult:
    """
    Represents a detection result.
    """

    def __init__(self, label, color, obj_type, confidence, location):
        """
        Stores information about an object detection.
        :param label: Detection label to be printed on the screen
        :param color: Rectangular and text color
        :param obj_type: What is the type of the object that was detected.
        :param confidence: What id the confidence of the detection
        :param location: Object location in the screen
        """
        self.label = label
        self.color = color
        self.obj_type = obj_type
        self.confidence = confidence
        self.location = location


class ObjectDetector:
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    def __init__(self, data_path, confidence):
        """
        :param data_path: Where is the pretrained CNN located.
        :param confidence: What is the minimum confidence needed to approve a detection.
        model: Pretrained model to detect objects.
        Classes: List of possible detections.
    	Colors: Containing a color for each possible detection type.
        """
        self.prototxt = data_path + "/" + "MobileNetSSD_deploy.prototxt.txt"
        self.model = data_path + "/" + "MobileNetSSD_deploy.caffemodel"
        self.model = self.load_model()
        self.confidence = confidence

    def load_model(self):
        """
        :return: Pretrained model loaded from file.
        """
        return cv2.dnn.readNetFromCaffe(self.prototxt, self.model)

    def detect(self, base_frame):
        """
        :param base_frame: Frame to run detector on
        :return: List of object detections
        """
        # grab the frame dimensions and convert it to a blob
        frame = base_frame
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                     0.007843, (300, 300), cv2.CV_8U)  # 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        self.model.setInput(blob)
        detections = self.model.forward()
        results = []
        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > self.confidence:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                coordinates = box.astype("int")
                # (startX, startY, endX, endY) = coordinates
                # # draw the prediction on the frame
                obj_type = ObjectDetector.CLASSES[idx]
                label = "{}: {:.2f}%".format(ObjectDetector.CLASSES[idx], confidence * 100)
                # cv2.rectangle(frame, (startX, startY), (endX, endY), ObjectDetector.COLORS[idx], 2)
                # y = startY - 15 if startY - 15 > 15 else startY + 15
                # cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ObjectDetector.COLORS[idx], 2)
                color = ObjectDetector.COLORS[idx]
                results.append(DetectionResult(label, color, obj_type, confidence, coordinates))
        return frame, results


if __name__ == '__main__':
    # cap = cv2.VideoCapture(0)
    detector = ObjectDetector(".", 0.7)
    detections = ""
    frame = cv2.imread("../left_frame.jpg")
    frame, left_results = detector.detect(frame)

    frame = cv2.imread("../right_frame.jpg")
    frame, right_results = detector.detect(frame)

    while True:
        ret, frame = cap.read()
        if ret:
            detections = detector.detect(frame)
            cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        elif cv2.waitKey(1) & 0xFF == ord('s'):
            print(detections.shape)
            print(detections[0, 0, 1, 1])
