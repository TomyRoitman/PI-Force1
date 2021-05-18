import sys

import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage


class Stream(QMainWindow):
    def __init__(self):
        super(Stream, self).__init__()
        loadUi("stream.ui", self)

    def show_stream(self, img, width, height):
        bytesPerLine = 3 * width
        img = np.require(img, np.uint8, 'C')
        pic = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pix = QPixmap()
        pix = pix.fromImage(pic)
        smaller_pixmap = pix.scaled(200, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        print(smaller_pixmap)
        label = QtWidgets.QLabel()
        label.setPixmap(smaller_pixmap)


def initialize():
    app = QApplication(sys.argv)
    stream = Stream()
    widgets = QtWidgets.QStackedWidget()

    widgets.addWidget(stream)
    widgets.show()
    app.exec_()


if __name__ == '__main__':
    main()
