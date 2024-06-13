#!/usr/bin/python

"""
Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QGridLayout,
    QVBoxLayout,
    QWidget
    )

# local imports
from .vacuum import QVacuumWidget
from .plane import QPlanePositioningWidget
from .height import QZMotionWidget
from .lense import QLenseMotionWidget
from .climate import QAHTWidget
from .LED import QLEDWidget
from .listener import Listener

class QPositioningTab(QWidget):

    def __init__(self, config, ESP):
        
        self.config = config
        self.ESP = ESP

        super().__init__()
        self.initUI()

        self.resources = {
            "DRX": self.plane_positioning_widget,
            "DRY": self.plane_positioning_widget,
            "DRZ": self.z_motion_widget,
            "DRL": self.lense_motion_widget,
            "AHT": self.AHT_widget,
            "RLD": self.RLED_widget,
            "BLD": self.BLED_widget,
            "TMG": TaskManager()
        }
        self.listener = Listener(self.config, self.ESP, self.resources)

    def initUI(self):
    
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # self.vacuum_widget = QVacuumWidget(self.config, self.ESP)
        # self.grid.addWidget(self.vacuum_widget, 0, 0)

        self.lense_motion_widget = QLenseMotionWidget(self.config, self.ESP)
        self.grid.addWidget(self.lense_motion_widget, 0, 0)

        self.z_motion_widget = QZMotionWidget(self.config, self.ESP)
        self.grid.addWidget(self.z_motion_widget, 1, 0)

        self.plane_positioning_widget = QPlanePositioningWidget(self.config, self.ESP)
        self.grid.addWidget(self.plane_positioning_widget, 2, 0)

        self.vbox = QVBoxLayout()
        self.grid.addLayout(self.vbox, 0, 1, 3, 1)

        self.AHT_widget = QAHTWidget(self.config, self.ESP)
        self.vbox.addWidget(self.AHT_widget, 0)

        self.RLED_widget = QLEDWidget(self.config, self.ESP, name="RLD", label="Red LED")
        self.BLED_widget = QLEDWidget(self.config, self.ESP, name="BLD", label="Blue LED")
        self.vbox.addWidget(self.RLED_widget, 1)
        self.vbox.addWidget(self.BLED_widget, 1)

class TaskManager:

    def update_UI(self, command, arguments):
        pass