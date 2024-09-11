from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

import time
import numpy as np

from backend.resources.manager import QResourceManager
from config.init_config import init_config
from exposure.API.rasp0 import QRaspZero

class ExpoThread(QThread):

    def __init__(self, ):
        super().__init__()
        self._run_flag = True

    def run(self):

        for x in range(0, self.width, self.x_step):
                
            for y in range(0, self.height, self.y_step):

                print(f"setting pixels up to ({x+self.x_step}, {y+self.y_step})")

                self.rasp0.set_pixels(0, x+self.x_step, 0, y+self.y_step, 1)
                time.sleep(0.5)

        self.start_pb.setDisabled(False)


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class App(QWidget):
    def __init__(self):

        self.config = init_config("config")
        self.rm = QResourceManager(self.config)

        self.rm.update_resource("rasp0", QRaspZero)
        self.rasp0 = self.rm["rasp0"]
        self.rasp0.connect()

        self.width = 720
        self.height = 1280
        self.x_step = 160
        self.y_step = 160

        super().__init__()
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Webcam')

        self.start_pb = QPushButton("Start")
        self.start_pb.clicked.connect(self.on_test_start)

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.start_pb)
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.textLabel)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def on_test_start(self):

        self.start_pb.setDisabled(True)
        self.test_thread = ExpoThread()
        self.e


    def closeEvent(self, event):
        self.thread.stop()
        event.accept()



    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
