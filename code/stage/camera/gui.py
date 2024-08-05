# third-party imports
import cv2
import numpy as np

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QLabel,
    QGridLayout,
    QGroupBox
    )

class VideoThread(QThread):
    
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while True:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)

class QCameraWidget(QGroupBox):

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager
        # self.cam_address = self.config["Camera"]["address"]

        super().__init__("Camera")

        self.initUI()
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.image_lab = QLabel(self)
        self.image_width = self.config["image_width"]
        
        empty_arr = np.float32(np.ones(shape=(480, 640)))
        empty_img = self.convert_cv_qt(empty_arr)

        self.image_lab.setPixmap(empty_img)
        self.grid.addWidget(self.image_lab, 0, 0, alignment=Qt.AlignCenter)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_lab with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_lab.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data,
            w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaledToWidth(self.image_width)
        return QPixmap.fromImage(p)
