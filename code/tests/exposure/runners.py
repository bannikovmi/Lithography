import time

import numpy as np
import cv2 as cv

from PyQt5.QtCore import pyqtSignal, QObject, QRunnable

T_DELAY = 0.3
MAX_SCAN_COUNTER = 300

class ExpoSignals(QObject):

    finished = pyqtSignal()
    status_changed = pyqtSignal(str)
    frame_updated = pyqtSignal(np.ndarray)

class ExpoRunner(QRunnable):

    def __init__(self, rasp0, scan_params, dir_path):
        
        super().__init__()

        self.signals = ExpoSignals()

        self.rasp0 = rasp0
        self.scan_params = scan_params
        self.dir_path = dir_path

        self._run_flag = True

        self.matrix_width = 1920
        self.matrix_height = 1080

        self.pts1 = np.float32([[569.2, 383.0], [572.6, 676.8], [1089.2, 377.3]])
        self.pts2 = np.float32([[0, 0], [0, self.matrix_height], [self.matrix_width, 0]])
        self.affine_matrix = cv.getAffineTransform(self.pts1, self.pts2)

    def run(self):

        # Connect 
        self.rasp0.connect()
        self.cap = cv.VideoCapture(0)

        self.signals.status_changed.emit("Connecting to rasp0 and cam")
        time.sleep(5)

        # set cam resolution
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

        x_params = self.scan_params["x"]
        y_params = self.scan_params["y"]
        i_params = self.scan_params["i"]

        x_step = x_params["step"]
        y_step = y_params["step"]
        i_step = i_params["step"]

        # save light pictures of different intensity
        for i in range(0, 256, i_step):

            if not self._run_flag:
                break

            self.signals.status_changed.emit(f"full {i}")
            self.rasp0.set_pixels(0, 0, 720, 1280, i)
                
            time.sleep(T_DELAY)

            cv_img = self.get_frame()
            cv.imwrite(f"{self.dir_path}/full_{i}.png", cv_img)

        # set zero intensity
        self.signals.status_changed.emit(f"full 0")
        self.rasp0.set_pixels(0, 0, 720, 1280, 0)
        time.sleep(T_DELAY)

        cv_img = self.get_frame()

        self.scan_counter = 0

        for x in range(x_params["start"], x_params["stop"], x_step):
                
            for y in range(y_params["start"], y_params["stop"], y_step):

                for i in range(i_params["start"], i_params["stop"], i_params["step"]):

                    if not self._run_flag:
                        break

                    self.signals.status_changed.emit(f"at ({x}, {y}), int={i}, {self.scan_counter}:{MAX_SCAN_COUNTER}")
                    self.rasp0.set_pixels(x, y, x+x_step, y+y_step, i)
                    self.scan_counter += 1
                    
                    time.sleep(T_DELAY)

                    cv_img = self.get_frame()                
                    cv.imwrite(f"{self.dir_path}/{x}_{y}_{i}.png", cv_img)

                # check scan counter
                if self.scan_counter > MAX_SCAN_COUNTER:
                    self.reboot_proj()

                # dark pixels
                self.rasp0.set_pixels(x, y, x+x_step, y+y_step, 0)
                time.sleep(T_DELAY)
                cv_img = self.get_frame()

                if not self._run_flag:
                    break

            if not self._run_flag:
                break

        self.signals.finished.emit()

    def get_frame(self):

        # Skip 4 frames
        for i in range(5):
            self.cap.grab()

        _, cv_img = self.cap.read()
        cv_img = self.transform_pic(cv_img)
        self.signals.frame_updated.emit(cv_img)

        return cv_img

    def transform_pic(self, img):

        return cv.warpAffine(img, self.affine_matrix, (self.matrix_width, self.matrix_height))

    def reboot_proj(self):

        self.scan_counter = 0
        self.signals.status_changed.emit("rebooting projector")
        self.rasp0.end_loop()
        time.sleep(5)
        self.rasp0.start_loop()
        time.sleep(5)

class VideoSignals(QObject):

    change_pixmap_signal = pyqtSignal(np.ndarray)

class VideoRunner(QRunnable):

    def __init__(self):
        
        self.signals = VideoSignals()
        super().__init__()
        self._run_flag = True

    def run(self):

        # capture from web cam
        cap = cv.VideoCapture(0)

        cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.signals.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
