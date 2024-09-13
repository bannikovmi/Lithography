import os
import sys
import time

import json
import cv2 as cv
import numpy as np

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThreadPool
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget
)

from backend.resources.manager import QResourceManager
from config.init_config import init_config
from exposure.API.rasp0 import QRaspZero

from tests.exposure.runners import ExpoRunner
from tests.exposure.scanner import QVarScannerGB

class App(QWidget):

    def __init__(self):

        self.thread_pool = QThreadPool.globalInstance()

        self.res_config = init_config("config")
        with open("tests/exposure/config.json", "r") as file:
            self.config = json.load(file)

        self.rm = QResourceManager(self.res_config)

        self.rm.update_resource("rasp0", QRaspZero)
        self.rasp0 = self.rm["rasp0"]

        self.display_width = 854
        self.display_height = 480

        super().__init__()
        self.initUI()

    def initUI(self):
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width, self.display_height)

        self.start_pb = QPushButton("Start")
        self.start_pb.clicked.connect(self.on_test_start)

        #################################################################################
        ### Labels and spinboxes
        #################################################################################   
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        vbox.addWidget(self.start_pb)

        self.x_scanner = QVarScannerGB(self.config["x"])
        self.y_scanner = QVarScannerGB(self.config["y"])
        self.i_scanner = QVarScannerGB(self.config["i"])

        vbox.addWidget(self.x_scanner)
        vbox.addWidget(self.y_scanner)
        vbox.addWidget(self.i_scanner)

        vbox.addWidget(self.image_label)

    def on_test_start(self):

        self.frame_counter = 0

        scan_params = {
            "x": self.x_scanner.get_params(),
            "y": self.y_scanner.get_params(),
            "i": self.i_scanner.get_params(),
        }

        x_name = self.x_scanner.get_fname()
        y_name = self.y_scanner.get_fname()
        i_name = self.i_scanner.get_fname()

        dir_path = f"../data/proj_scans/{x_name}-{y_name}-{i_name}"
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        self.start_pb.setText("Abort")
        self.start_pb.clicked.disconnect()
        self.start_pb.clicked.connect(self.on_test_abort)

        self.expo_runner = ExpoRunner(self.rasp0, scan_params, dir_path)
        self.expo_runner.signals.finished.connect(self.on_test_finish)
        self.expo_runner.signals.status_changed.connect(self.setWindowTitle)
        self.expo_runner.signals.frame_updated.connect(self.update_image)

        self.thread_pool.start(self.expo_runner)

    def on_test_abort(self):

        self.expo_runner._run_flag = False

    def on_test_finish(self):

        self.clear()
        self.start_pb.setText("Start")
        self.start_pb.clicked.disconnect()
        self.start_pb.clicked.connect(self.on_test_start)
        self.rasp0.end_loop()
        self.rasp0.disconnect()

    def clear(self):

        self.rasp0.set_pixels(0, 0, 720, 1280, 0)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):

        self.frame_counter += 1
        print(f"main: updating image, frame: {self.frame_counter}")

        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
