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
    QSpinBox
    )

# local imports
from stage.exposure.API import QRaspZero

class QProjectorWidget(QGroupBox):

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager
        self.rm.update_resource("rasp0", QRaspZero)
        self.rasp0 = self.rm["rasp0"]

        self.rasp0.connect()
        self.rasp0.init_projector()

        super().__init__(self.config["label"])

        self.initUI()
        self.connect_signals()

    def initUI(self):
    
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.expose_pb = QPushButton("Expose")
        self.upload_pb = QPushButton("Upload file")
        self.selector = QListWidget()
        # self.selector.setReadOnly(True)

        self.exp_time_lab = QLabel("Exposure time (ms)")
        self.exp_time_sb = QSpinBox()

        self.grid.addWidget(self.expose_pb, 0, 0)
        self.grid.addWidget(self.upload_pb, 1, 0)
        self.grid.addWidget(self.exp_time_lab, 0, 1)
        self.grid.addWidget(self.exp_time_sb, 0, 2)
        self.grid.addWidget(self.selector, 1, 1, 1, 2)

        # Set widgets config
        self.exp_time_sb.setMinimum(self.config["min_exp_time"])
        self.exp_time_sb.setMaximum(self.config["max_exp_time"])
        self.exp_time_sb.setValue(self.config["init_exp_time"])

        # Populate list widget with picture names from remote machine
        self.populate_listview()

    def closeEvent(self, event):

        self.rasp0.stop_projector()
        event.accept()

    def connect_signals(self):

        self.upload_pb.clicked.connect(self.show_upload_dialog)
        self.expose_pb.clicked.connect(self.expose_pic)

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
