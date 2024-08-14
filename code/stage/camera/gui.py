# third-party imports
import cv2 as cv
import numpy as np

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QCheckBox,
    QLabel,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction
    )

# local imports
from widgets.numeric import QNumericControl

from .API import QCamera

class QCameraWidget(QGroupBox):

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager
        self.rm.update_resource("cam", QCamera)
        self.cam = self.rm["cam"]
        self.cam.start()

        super().__init__("Camera")

        self.initUI()
        self.connect_signals()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.hbox = QHBoxLayout()
        self.grid.addLayout(self.hbox, 0, 0)

        self.settings_pb = QPushButton("Settings")
        self.hbox.addWidget(self.settings_pb)
        self.hbox.addStretch(1)

        self.image_lab = QLabel(self)
        self.image_width = self.config["image_width"]
        
        # Set widget params
        self.settings_menu = QMenu()
        self.settings_pb.setMenu(self.settings_menu)

        self.settings_qwa = QWidgetAction(self.settings_menu)
        self.camera_settings = QCameraSettings(self.config, self.cam)
        self.settings_qwa.setDefaultWidget(self.camera_settings)
        self.settings_menu.addAction(self.settings_qwa)

        empty_arr = np.float32(np.ones(shape=(480, 640)))
        empty_img = self.convert_cv_qt(empty_arr)

        self.image_lab.setPixmap(empty_img)
        self.grid.addWidget(self.image_lab, 1, 0, alignment=Qt.AlignCenter)

    def connect_signals(self):

        self.cam.frame_updated.connect(self.update_image)

    def on_capture_start(self):

        self.start_pb.clicked.disconnect(self.on_capture_start)
        self.start_pb.clicked.connect(self.on_capture_release)
        self.start_pb.setText("Release video capture")
        self.cam.start()

    def on_capture_release(self):

        self.start_pb.clicked.disconnect(self.on_capture_release)
        self.start_pb.clicked.connect(self.on_capture_start)
        self.start_pb.setText("Start video capture")
        self.cam.release()

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data,
            w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaledToWidth(self.image_width)
        return QPixmap.fromImage(p)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_lab with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_lab.setPixmap(qt_img)

class QCameraSettings(QWidget):

    def __init__(self, config, cam):

        self.config = config
        self.cam = cam

        super().__init__()
        self.initUI()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.restore_pb = QPushButton("Restore default values")
        self.vbox.addWidget(self.restore_pb)

        self.hbox = QHBoxLayout()
        self.vbox.addLayout(self.hbox)

        # Auto white balance
        self.auto_wb_cb = QCheckBox("Auto white balance")
        self.auto_wb_cb.setChecked(self.config["auto_wb"])
        self.hbox.addWidget(self.auto_wb_cb)

        # Auto-exposure
        self.auto_exp_cb = QCheckBox("Auto exposure")
        self.auto_exp_cb.setChecked(self.config["auto_exp"])
        self.hbox.addWidget(self.auto_exp_cb)

        self.param_controls = {}

        for key, val in self.config.items():
            
            if isinstance(val, dict):
            
                num_control = QNumericControl(val["label"])
                num_control.setMinimum(val["min"])
                num_control.setMaximum(val["max"])
                num_control.setSingleStep(val["step"])
                num_control.setDecimals(0)
            
                self.vbox.addWidget(num_control)
                self.param_controls[key] = num_control

    def connect_signals(self):

        self.auto_exp_cb.clicked.connect(self.on_auto_exp)
        self.auto_wb_cb.clicked.connect(self.on_auto_wb)
        for key, ctrl in self.param_controls.items():
            # Note the use of named argument key=key inside lambda function. For more info see
            # https://www.pythonguis.com/tutorials/transmitting-extra-data-qt-signals
            ctrl.valueChanged.connect(lambda val, key=key: setattr(self.cam, key, val)) 
        self.restore_pb.clicked.connect(self.set_default_values)

    def set_default_values(self):

        self.auto_exp_cb.setChecked(self.config["auto_exp"])
        self.auto_wb_cb.setChecked(self.config["auto_wb"])
        self.on_auto_exp()
        self.on_auto_wb()

        for key, ctrl in self.param_controls.items():
            ctrl.setValue(self.config[key]["default"])

    #     # White balance temperature
    #     self.wb_temp_ctr = QNumericControl(label="WB temperature [K]")
    #     self.wb_temp_ctr.setMinimum(self.config["wb_temp"]["min"])
    #     self.wb_temp_ctr.setMaximum(self.config["wb_temp"]["max"])
    #     self.wb_temp_ctr.setSingleStep(self.config["wb_temp"]["step"])
    #     self.wb_temp_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.wb_temp_ctr)

    #     # Brightness
    #     self.brightness_ctr = QNumericControl(label="Brightness")
    #     self.brightness_ctr.setMinimum(self.config["brightness"]["min"])
    #     self.brightness_ctr.setMaximum(self.config["brightness"]["max"])
    #     self.brightness_ctr.setSingleStep(self.config["brightness"]["step"])
    #     self.brightness_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.brightness_ctr)

    #     # Backlight compensation
    #     self.backlight_comp_ctr = QNumericControl(label="Backlight compensation")
    #     self.backlight_comp_ctr.setMinimum(self.config["backlight_comp"]["min"])
    #     self.backlight_comp_ctr.setMaximum(self.config["backlight_comp"]["max"])
    #     self.backlight_comp_ctr.setSingleStep(self.config["backlight_comp"]["step"])
    #     self.backlight_comp_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.backlight_comp_ctr)
        
    #     # White balance temperature
    #     self.contrast_ctr = QNumericControl(label="Contrast")
    #     self.contrast_ctr.setMinimum(self.config["contrast"]["min"])
    #     self.contrast_ctr.setMaximum(self.config["contrast"]["max"])
    #     self.contrast_ctr.setSingleStep(self.config["contrast"]["step"])
    #     self.contrast_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.contrast_ctr)
        
    #     # Auto-exposure
    #     self.auto_exp_cb = QCheckBox("Auto exposure")
    #     self.auto_exp_cb.setChecked(self.config["auto_exp"])
    #     self.vbox.addWidget(self.auto_exp_cb)

    #     # Exposure
    #     self.exposure_ctr = QNumericControl(label="Exposure time [ms]")
    #     self.exposure_ctr.setMinimum(self.config["exposure"]["min"])
    #     self.exposure_ctr.setMaximum(self.config["exposure"]["max"])
    #     self.exposure_ctr.setSingleStep(self.config["exposure"]["step"])
    #     self.exposure_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.exposure_ctr)

    #     # Gain
    #     self.gain_ctr = QNumericControl(label="Gain")
    #     self.gain_ctr.setMinimum(self.config["gain"]["min"])
    #     self.gain_ctr.setMaximum(self.config["gain"]["max"])
    #     self.gain_ctr.setSingleStep(self.config["gain"]["step"])
    #     self.gain_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.gain_ctr)

    #     # Gamma
    #     self.gamma_ctr = QNumericControl(label="Gamma")
    #     self.gamma_ctr.setMinimum(self.config["gamma"]["min"])
    #     self.gamma_ctr.setMaximum(self.config["gamma"]["max"])
    #     self.gamma_ctr.setSingleStep(self.config["gamma"]["step"])
    #     self.gamma_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.gamma_ctr)

    #     # Hue
    #     self.hue_ctr = QNumericControl(label="Hue")
    #     self.hue_ctr.setMinimum(self.config["hue"]["min"])
    #     self.hue_ctr.setMaximum(self.config["hue"]["max"])
    #     self.hue_ctr.setSingleStep(self.config["hue"]["step"])
    #     self.hue_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.hue_ctr)

    #     # Saturation
    #     self.saturation_ctr = QNumericControl(label="Saturation")
    #     self.saturation_ctr.setMinimum(self.config["saturation"]["min"])
    #     self.saturation_ctr.setMaximum(self.config["saturation"]["max"])
    #     self.saturation_ctr.setSingleStep(self.config["saturation"]["step"])
    #     self.saturation_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.saturation_ctr)

    #     # Sharpness
    #     self.sharpness_ctr = QNumericControl(label="Sharpness")
    #     self.sharpness_ctr.setMinimum(self.config["sharpness"]["min"])
    #     self.sharpness_ctr.setMaximum(self.config["sharpness"]["max"])
    #     self.sharpness_ctr.setSingleStep(self.config["sharpness"]["step"])
    #     self.sharpness_ctr.setDecimals(0)
    #     self.vbox.addWidget(self.sharpness_ctr)


    #     self.auto_exp_cb.clicked.connect(self.on_auto_exp)
    #     self.auto_wb_cb.clicked.connect(self.on_auto_wb)
    #     self.wb_temp_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "wb_temp", val))
    #     self.exposure_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "exposure", val))
    #     self.brightness_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "brightness", val))
    #     self.backlight_comp_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "backlight_comp", val))
    #     self.contrast_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "contrast", val))
    #     self.gain_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "gain", val))
    #     self.gamma_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "gamma", val))
    #     self.hue_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "hue", val))
    #     self.saturation_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "saturation", val))
    #     self.sharpness_ctr.valueChanged.connect(lambda val:
    #         setattr(self.cam, "sharpness", val))

    #     self.on_auto_exp()
    #     self.on_auto_wb()

    #     self.wb_temp_ctr.setValue(self.config["wb_temp"]["default"])
    #     self.brightness_ctr.setValue(self.config["brightness"]["default"])
    #     self.backlight_comp_ctr.setValue(self.config["backlight_comp"]["default"])
    #     self.contrast_ctr.setValue(self.config["contrast"]["default"])
    #     self.exposure_ctr.setValue(self.config["exposure"]["default"])
    #     self.gain_ctr.setValue(self.config["gain"]["default"])
    #     self.gamma_ctr.setValue(self.config["gamma"]["default"])
    #     self.hue_ctr.setValue(self.config["hue"]["default"])
    #     self.saturation_ctr.setValue(self.config["saturation"]["default"])
    #     self.sharpness_ctr.setValue(self.config["sharpness"]["default"])

    def on_auto_exp(self):

        if self.auto_exp_cb.isChecked():
            self.param_controls["exposure"].setDisabled(True)
            self.cam.auto_exp = True
        else:
            self.param_controls["exposure"].setDisabled(False)
            self.cam.auto_exp = False
            self.cam.exposure = self.param_controls["exposure"].value()

    def on_auto_wb(self):

        if self.auto_wb_cb.isChecked():
            self.param_controls["wb_temp"].setDisabled(True)
            self.cam.auto_wb = True
        else:
            self.param_controls["wb_temp"].setDisabled(False)
            self.cam.auto_wb = False
            self.cam.wb_temp = self.param_controls["wb_temp"].value()

