from collections import deque

# third-party imports
import cv2 as cv
import numpy as np

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
    QGridLayout,
    QGroupBox,
    QMenu,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidgetAction
    )

# local imports
from stage.camera.GUI.settings import QCameraSettings
from stage.camera.GUI.illumination import QIlluminationGB

from stage.camera.API.camera import QCamera
from stage.camera.API.processing import QImageProcessor

class QCameraGB(QGroupBox):

    var_updated = pyqtSignal(float)

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager

        super().__init__("Camera")
        
        self.rm.update_resource("cam", QCamera)
        self.cam = self.rm["cam"]
        self.cam.start()
        self.image_proc = QImageProcessor(self.config["image_proc"])

        self.show_rect = False
        self.show_cross = False
        self.focus_rect = None

        self.initUI()
        self.connect_signals()

    def initUI(self):

        # Create widgets
        self.illumination_gb = QIlluminationGB(self.config["illumination"], self.rm)

        # Settings
        self.settings_pb = QPushButton("Settings")
        self.settings_menu = QMenu()
        self.settings_pb.setMenu(self.settings_menu)

        self.settings_qwa = QWidgetAction(self.settings_menu)
        self.camera_settings = QCameraSettings(self.config["settings"], self.cam)
        self.settings_qwa.setDefaultWidget(self.camera_settings)
        self.settings_menu.addAction(self.settings_qwa)

        # Pixmap
        self.image_lab = QLabel(self)
        self.image_width = self.config["image_width"]

        # Pic crop
        self.crop_cb = QCheckBox("Crop to projector")

        # Create and fill layouts
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        
        self.vbox = QVBoxLayout()
        self.grid.addLayout(self.vbox, 0, 0, 2, 1)

        self.vbox.addWidget(self.settings_pb)
        self.vbox.addWidget(self.illumination_gb)
        self.vbox.addWidget(self.crop_cb)
        self.vbox.addStretch(1)

        self.grid.addWidget(self.image_lab, 0, 1, 2, 1, alignment=Qt.AlignRight)

        # Configurate widgets
        empty_arr = np.float32(np.ones(shape=(480, 640)))
        empty_img = self.convert_cv_qt(empty_arr)

        self.image_lab.setPixmap(empty_img)

        # self.af_menu = QMenu()
        # self.af_pb.setMenu(self.af_menu)

        # self.af_wa = QWidgetAction(self.af_menu)
        # self.af_widget = QAutofocusWidget(self.config["autofocus"], self.rm)
        # self.af_wa.setDefaultWidget(self.af_widget)
        # self.af_menu.addAction(self.af_wa)

        # self.avg_sb.setMinimum(self.config["avg_var"]["min"])
        # self.avg_sb.setMaximum(self.config["avg_var"]["max"])
        # self.avg_sb.setSingleStep(self.config["avg_var"]["step"])
        # self.avg_sb.setValue(self.config["avg_var"]["default"])

    def connect_signals(self):

        self.cam.frame_updated.connect(self.update_image)
        # self.var_updated.connect(self.af_widget.var_updated)
        # self.avg_sb.valueChanged.connect(lambda avg:
        #     setattr(self, "deq", deque(self.deq, maxlen=avg)))
        # self.af_widget.opt_z_updated.connect(lambda val:
        #     self.opt_z_le.setText(f"{val:.2f}"))

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

        # Perform laplacian transform and update variance
        laplacian = self.image_proc.laplacian(cv_img, self.focus_rect)
        self.var_updated.emit(laplacian.var())

        # If necessary, draw a rectangle and/or crosses at the vortices
        if self.show_rect:
            self.image_proc.draw_rect(cv_img, self.focus_rect)
        if self.show_cross:
            self.image_proc.draw_crosses(cv_img, self.focus_rect)

        # crop picture if necessary
        if self.crop_cb.isChecked():
            self.image_proc.crop(cv_img)

        # Convert cv_img to qt_img and set pixmap
        qt_img = self.convert_cv_qt(cv_img)
        self.image_lab.setPixmap(qt_img)

    def closeEvent(self, event):

        # Turn illumination off
        self.illumination_gb.illuminator.set("duty", 0)