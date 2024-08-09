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

    @property
    def backlight_comp(self):
        return self.cap.get(cv.CAP_PROP_BACKLIGHT)

    @backlight_comp.setter
    def backlight_comp(self, val):
        self.cap.set(cv.CAP_PROP_BACKLIGHT, val)

    @property
    def brightness(self):
        return self.cap.get(cv.CAP_PROP_BRIGHTNESS)

    @brightness.setter
    def brightness(self, val):
        self.cap.set(cv.CAP_PROP_BRIGHTNESS, val)

    @property
    def contrast(self):
        return self.cap.get(cv.CAP_PROP_CONTRAST)

    @contrast.setter
    def contrast(self, val):
        self.cap.set(cv.CAP_PROP_CONTRAST, val)

    @property
    def fps(self):
        return self.cap.get(cv.CAP_PROP_FPS)

    @property
    def exposure(self):
        return self.cap.get(cv.CAP_PROP_EXPOSURE)

    @exposure.setter
    def exposure(self, val):
        self.cap.set(cv.CAP_PROP_EXPOSURE, val)

    @property
    def gamma(self):
        return self.cap.get(cv.CAP_PROP_GAMMA)

    @gamma.setter
    def gamma(self, val):
        self.cap.set(cv.CAP_PROP_GAMMA, val)

    @property
    def gain(self):
        return self.cap.get(cv.CAP_PROP_GAIN)

    @gain.setter
    def gain(self, val):
        self.cap.set(cv.CAP_PROP_GAIN, val)

    @property
    def height(self):
        return self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)

    @property
    def hue(self):
        return self.cap.get(cv.CAP_PROP_HUE)

    @hue.setter
    def hue(self, val):
        self.cap.set(cv.CAP_PROP_HUE, val)

    @property
    def saturation(self):
        return self.cap.get(cv.CAP_PROP_SATURATION)

    @saturation.setter
    def saturation(self, val):
        self.cap.set(cv.CAP_PROP_SATURATION, val)

    @property
    def sharpness(self):
        return self.cap.get(cv.CAP_PROP_SHARPNESS)

    @sharpness.setter
    def sharpness(self, val):
        self.cap.set(cv.CAP_PROP_SHARPNESS, val)

    @property
    def wb_temp(self):
        return self.cap.get(cv.CAP_PROP_WB_TEMPERATURE)

    @wb_temp.setter
    def wb_temp(self, val):
        self.cap.set(cv.CAP_PROP_WB_TEMPERATURE, val)

    @property
    def width(self):
        return self.cap.get(cv.CAP_PROP_FRAME_WIDTH)

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
