# old_codec = 1448695129
# new_codec = 0x47504A4D

# standard library imports
from enum import Enum

# third-party imports
import cv2 as cv
import numpy as np

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, QThreadPool

# local imports
from backend.resources.resource import QResource

class RunnerSignals(QObject):

    frame_updated = pyqtSignal(np.ndarray)

class CaptureRunner(QRunnable):

    def __init__(self, cap):

        super().__init__()

        self.cap = cap
        self.signals = RunnerSignals()
        self.is_finished = False

    def run(self):

        while not self.is_finished:
            ret, cv_img = self.cap.read()
            if ret:
                self.signals.frame_updated.emit(cv_img)

class AutoExpMode(Enum):

    MANUAL = 1
    APERTURE_PRIORITY = 3

    @classmethod
    def from_bool(cls, val):
        if val:
            return cls(3)
        else:
            return cls(1)

    def to_bool(self):
        if self.value == 3:
            return True
        else:
            return False

class QCamera(QResource):

    frame_updated = pyqtSignal(np.ndarray)

    props = {
        "backlight_comp": cv.CAP_PROP_BACKLIGHT,
        "brightness": cv.CAP_PROP_BRIGHTNESS,
        "contrast": cv.CAP_PROP_CONTRAST,
        "exposure": cv.CAP_PROP_EXPOSURE,
        "gamma": cv.CAP_PROP_GAMMA,
        "gain": cv.CAP_PROP_GAIN,
        "hue": cv.CAP_PROP_HUE,
        "saturation": cv.CAP_PROP_SATURATION,
        "sharpness": cv.CAP_PROP_SHARPNESS,
        "wb_temp": cv.CAP_PROP_WB_TEMPERATURE
    }

    def __init__(self, resource):

        # Reinitialize base class resource
        self.name = resource.name
        self.master_int = resource.master_int
        self.config = resource.config

        super().__init__(self.name, self.master_int)

        # Global thread pool instance
        self.thread_pool = QThreadPool.globalInstance()

        # Starti videocapture
        self.cap = cv.VideoCapture(0)

    def start(self):
        
        self.capture_runner = CaptureRunner(self.cap)
        self.capture_runner.signals.frame_updated.connect(self.frame_updated)

        self.thread_pool.start(self.capture_runner)

    def release(self):
        
        self.capture_runner.is_finished = True
        self.cap.release()

    ##########################################################################################
    ### Camera properties
    ##########################################################################################
    def set(self, prop, val):
        self.cap.set(self.props[prop], val)

    def get(self, prop):
        return self.cap.get(self.props[prop])

    @property
    def auto_exp(self):
        return AutoExpMode(self.cap.get(cv.CAP_PROP_AUTO_EXPOSURE)).to_bool()

    @auto_exp.setter
    def auto_exp(self, val):
        self.cap.set(cv.CAP_PROP_AUTO_EXPOSURE, AutoExpMode.from_bool(val).value)

    @property
    def auto_wb(self):
        return bool(self.cap.get(cv.CAP_PROP_AUTO_WB))

    @auto_wb.setter
    def auto_wb(self, val):
        self.cap.set(cv.CAP_PROP_AUTO_WB, int(val))

# class QCameraWidget(QGroupBox):

#     def __init__(self, config):

#         self.config = config
#         # self.cam_address = self.config["Camera"]["address"]

#         super().__init__("Camera")

#         self.initUI()
#         self.thread = VideoThread()
#         self.thread.change_pixmap_signal.connect(self.update_image)
#         self.thread.start()

#     def initUI(self):

#         self.grid = QGridLayout()
#         self.setLayout(self.grid)

#         self.image_lab = QLabel(self)
#         self.image_width = self.config["Camera"]["image_width"]
        
#         empty_arr = np.float32(np.ones(shape=(480, 640)))
#         empty_img = self.convert_cv_qt(empty_arr)

#         self.image_lab.setPixmap(empty_img)
#         self.grid.addWidget(self.image_lab, 0, 0, alignment=Qt.AlignCenter)


    
#     def convert_cv_qt(self, cv_img):
#         """Convert from an opencv image to QPixmap"""
#         rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
#         h, w, ch = rgb_image.shape
#         bytes_per_line = ch * w
#         convert_to_Qt_format = QImage(rgb_image.data,
#             w, h, bytes_per_line, QImage.Format_RGB888)
#         p = convert_to_Qt_format.scaledToWidth(self.image_width)
#         return QPixmap.fromImage(p)
