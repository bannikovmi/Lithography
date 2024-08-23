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
    QHBoxLayout,
    QMenu,
    QPushButton,
    QWidgetAction
    )

# local imports
from .af_widget import QAutofocusWidget
from .cam_settings import QCameraSettings

from stage.camera.API.camera import QCamera
from stage.camera.API.processing import QImageProcessor

class QCameraWidget(QGroupBox):

    var_updated = pyqtSignal(float)

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager
        
        self.rm.update_resource("cam", QCamera)
        self.cam = self.rm["cam"]
        self.cam.start()
        self.image_proc = QImageProcessor(self.config["image_proc"])
        
        super().__init__("Camera")

        self.initUI()
        self.connect_signals()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.hbox = QHBoxLayout()
        self.grid.addLayout(self.hbox, 0, 0)

        self.settings_pb = QPushButton("Settings")
        self.af_pb = QPushButton("Autofocus")
        self.variance_lab = QLabel("Focus rectangle laplacian variance")
        self.variance_le = QLineEdit()
        self.variance_le.setReadOnly(True)
        
        self.hbox.addWidget(self.settings_pb)
        self.hbox.addWidget(self.af_pb)
        self.hbox.addWidget(self.variance_lab)
        self.hbox.addWidget(self.variance_le)

        self.hbox.addStretch(1)

        self.image_lab = QLabel(self)
        self.image_width = self.config["image_width"]
        
        # Set widget params
        self.settings_menu = QMenu()
        self.settings_pb.setMenu(self.settings_menu)

        self.settings_qwa = QWidgetAction(self.settings_menu)
        self.camera_settings = QCameraSettings(self.config["settings"], self.cam)
        self.settings_qwa.setDefaultWidget(self.camera_settings)
        self.settings_menu.addAction(self.settings_qwa)

        self.af_menu = QMenu()
        self.af_pb.setMenu(self.af_menu)

        self.af_wa = QWidgetAction(self.af_menu)
        self.af_widget = QAutofocusWidget(self.config["autofocus"], self.rm)
        self.af_wa.setDefaultWidget(self.af_widget)
        self.af_menu.addAction(self.af_wa)

        empty_arr = np.float32(np.ones(shape=(480, 640)))
        empty_img = self.convert_cv_qt(empty_arr)

        self.image_lab.setPixmap(empty_img)
        self.grid.addWidget(self.image_lab, 1, 0, alignment=Qt.AlignCenter)

    def connect_signals(self):

        self.cam.frame_updated.connect(self.update_image)
        self.var_updated.connect(self.af_widget.var_updated)

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
        laplacian = self.image_proc.laplacian(cv_img, self.af_widget.af_region.rect,
            transform_img = self.af_widget.af_region.transform_cb.isChecked())
        var = laplacian.var()
        self.variance_le.setText(f"{var:.2f}")
        self.var_updated.emit(var)
        
        # If necessary, draw a rectangle and/or crosses at the vortices
        if self.af_widget.af_region.show_rect_cb.isChecked():
            self.image_proc.draw_rect(cv_img, self.af_widget.af_region.rect)
        if self.af_widget.af_region.show_cross_cb.isChecked():
            self.image_proc.draw_crosses(cv_img, self.af_widget.af_region.rect)

        # Convert cv_img to qt_img and set pixmap
        qt_img = self.convert_cv_qt(cv_img)
        self.image_lab.setPixmap(qt_img)
