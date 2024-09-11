#!/usr/bin/python

"""
Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QWidget
    )

# local imports
# Widgets
from stage.camera.GUI.camera import QCameraGB
from stage.focus.GUI.focus import QFocusGB
from stage.drives.GUI.plane import QPlaneGB
from stage.drives.GUI.vertical import QVerticalGB
from stage.drives.GUI.lense import QLenseGB

# API elements
from stage.esp.esp import QESPPos

class QStageWidget(QWidget):

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager

        # Overwrite esp resource here so that widgets may use it upon initialization
        self.esp_pos = QESPPos(self.rm["esp_pos"])
        self.rm["esp_pos"] = self.esp_pos
        self.esp_pos.open()

        super().__init__()
        self.initUI()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):

        # Create widgets
        self.focus_gb = QFocusGB(self.config["focus"], self.rm)
        self.camera_gb = QCameraGB(self.config["camera"], self.rm)
        # self.projector_gb = QProjectorGB(self.config["projector"], self.rm)

        self.plane_gb = QPlaneGB(self.config["plane"], self.rm)
        self.vertical_gb = QVerticalGB(self.config["vertical"], self.rm)
        self.lense_gb = QLenseGB(self.config["lense"], self.rm)

        # Create layouts
        self.grid = QGridLayout()
        self.vbox = QVBoxLayout()
        self.grid.addLayout(self.vbox, 0, 0, 3, 1)
        self.setLayout(self.grid)

        # Fill layouts
        self.grid.addWidget(self.lense_gb, 0, 1)
        self.grid.addWidget(self.vertical_gb, 1, 1)
        self.grid.addWidget(self.plane_gb, 2, 1)

        self.vbox.addStretch(1)
        self.vbox.addWidget(self.focus_gb)
        self.vbox.addWidget(self.camera_gb)
        # self.vbox.addWidget(self.projector_gb)

        # Set layout stretch
        self.grid.setRowStretch(0, 1)
        self.grid.setRowStretch(1, 1)
        self.grid.setRowStretch(2, 1)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 0)

    def connect_signals(self):

        self.focus_gb.show_rect.connect(lambda state:
            setattr(self.camera_gb, "show_rect", state))
        self.focus_gb.show_cross.connect(lambda state:
            setattr(self.camera_gb, "show_cross", state))
        self.focus_gb.rect_updated.connect(lambda rect:
            setattr(self.camera_gb, "focus_rect", rect))

        self.camera_gb.var_updated.connect(self.focus_gb.var_updated)

    def set_default_values(self):

        rect = self.focus_gb.region_gb.update_rectangle()

    def closeEvent(self, event):
        
        self.plane_gb.closeEvent(event)
        self.lense_gb.closeEvent(event)
        self.vertical_gb.closeEvent(event)
        self.camera_gb.closeEvent(event)
