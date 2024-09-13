#!/usr/bin/python

"""
Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

import os

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QGridLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSpinBox,
    QWidget
    )

# local imports
from exposure.API.rasp0 import QRaspZero

class QExposureWidget(QWidget):

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager
        self.rm.update_resource("rasp0", QRaspZero)
        self.rasp0 = self.rm["rasp0"]

        self.rasp0.connect()
        # self.rasp0.init_projector()

        super().__init__()

        self.initUI()
        self.connect_signals()

    def initUI(self):
    
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        #################################################################################
        ### Expose from picture
        #################################################################################
        self.pic_gb = QGroupBox("Expose picture")
        self.pic_grid = QGridLayout()
        self.pic_gb.setLayout(self.pic_grid)
        self.grid.addWidget(self.pic_gb, 0, 0)

        self.expose_pb = QPushButton("Expose")
        self.upload_pb = QPushButton("Upload file")
        self.selector = QListWidget()
        # self.selector.setReadOnly(True)

        self.exp_time_lab = QLabel("Exposure time (ms)")
        self.exp_time_sb = QSpinBox()

        self.pic_grid.addWidget(self.upload_pb, 0, 0)
        self.pic_grid.addWidget(self.exp_time_lab, 0, 1)
        self.pic_grid.addWidget(self.exp_time_sb, 0, 2)
        self.pic_grid.addWidget(self.expose_pb, 0, 3)
        self.pic_grid.addWidget(self.selector, 1, 0, 1, 4)

        # Set widgets config
        self.exp_time_sb.setMinimum(self.config["min_exp_time"])
        self.exp_time_sb.setMaximum(self.config["max_exp_time"])
        self.exp_time_sb.setValue(self.config["init_exp_time"])

        #################################################################################
        ### Set pixels
        #################################################################################
        self.pix_gb = QGroupBox("Set pixels")
        self.pix_grid = QGridLayout()
        self.pix_gb.setLayout(self.pix_grid)
        self.grid.addWidget(self.pix_gb, 0, 1)

        self.x1_lab = QLabel("x1")
        self.y1_lab = QLabel("y1")
        self.x2_lab = QLabel("x2")
        self.y2_lab = QLabel("y2")

        self.x1_sb = QSpinBox()
        self.y1_sb = QSpinBox()
        self.x2_sb = QSpinBox()
        self.y2_sb = QSpinBox()

        self.pix_grid.addWidget(self.x1_lab, 0, 0)
        self.pix_grid.addWidget(self.y1_lab, 0, 2)
        self.pix_grid.addWidget(self.x2_lab, 1, 0)
        self.pix_grid.addWidget(self.y2_lab, 1, 2)

        self.pix_grid.addWidget(self.x1_sb, 0, 1)
        self.pix_grid.addWidget(self.y1_sb, 0, 3)
        self.pix_grid.addWidget(self.x2_sb, 1, 1)
        self.pix_grid.addWidget(self.y2_sb, 1, 3)

        self.int_lab = QLabel("Intensity")
        self.int_sb = QSpinBox()
        self.pix_grid.addWidget(self.int_lab, 0, 4)
        self.pix_grid.addWidget(self.int_sb, 0, 5)

        self.set_pb = QPushButton("Set")
        self.pix_grid.addWidget(self.set_pb, 1, 4, 1, 2)

        # Set ranges -- MOVE THIS TO CONFIG!!!
        self.x1_sb.setMaximum(720)
        self.x2_sb.setMaximum(720)
        self.y1_sb.setMaximum(1280)
        self.y2_sb.setMaximum(1280)
        self.int_sb.setMaximum(255)
        self.x2_sb.setValue(720)
        self.y2_sb.setValue(1280)
        #################################################################################
        ### Finalize
        #################################################################################
        # Populate list widget with picture names from remote machine
        self.populate_listview()

    def closeEvent(self, event):

        self.rasp0.stop_projector()

    def connect_signals(self):

        self.upload_pb.clicked.connect(self.show_upload_dialog)
        self.expose_pb.clicked.connect(self.expose_pic)

        self.set_pb.clicked.connect(self.set_pixels)

        self.rasp0.exposure_finished.connect(lambda: self.expose_pb.setDisabled(False))

    def expose_pic(self):

        self.expose_pb.setDisabled(True)
        self.rasp0.expose_remote(self.selector.currentItem().text(),
            self.exp_time_sb.value(), separate_thread=True)

    def show_upload_dialog(self):

        home_dir = os.path.join("stage", "exposure", "pics")
        fname = QFileDialog.getOpenFileName(self, 'Select file', home_dir)

        if fname[0]:
            self.rasp0.upload_pic(fname[0])
            self.populate_listview()

    def populate_listview(self):

        self.selector.clear()
        
        for name in self.rasp0.list_pics():
            self.selector.addItem(name)

        self.selector.setCurrentItem(self.selector.item(0))

    def set_pixels(self):

        x1 = self.x1_sb.value()
        y1 = self.y1_sb.value()
        x2 = self.x2_sb.value()
        y2 = self.y2_sb.value()
        i = self.int_sb.value()
        self.rasp0.set_pixels(x1, y1, x2, y2, i)

