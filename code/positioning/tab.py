#!/usr/bin/python

"""
Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QGridLayout,
    QVBoxLayout,
    QWidget
    )

# local imports
from .vacuum import QVacuumWidget
from .climate import QAHTWidget
from .LED import QLEDControlWidget
from .listener import Listener
from .motion import QMotionGB

class QPositioningTab(QWidget):

    def __init__(self, config, ESP):
        
        self.config = config
        self.ESP = ESP

        super().__init__()
        self.initUI()

        self.resources = {
            "DRX": self.x_motion_gb,
            "DRY": self.y_motion_gb,
            "DRZ": self.z_motion_gb,
            "DRL": self.lense_motion_gb,
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

        self.lense_motion_gb = QMotionGB(self.config, self.ESP, name="DRL")
        self.x_motion_gb = QMotionGB(self.config, self.ESP, name="DRX")
        self.y_motion_gb = QMotionGB(self.config, self.ESP, name="DRY")
        self.z_motion_gb = QMotionGB(self.config, self.ESP, name="DRZ")

        self.grid.addWidget(self.x_motion_gb, 1, 1)
        self.grid.addWidget(self.y_motion_gb, 1, 0)
        self.grid.addWidget(self.lense_motion_gb, 0, 1)
        self.grid.addWidget(self.z_motion_gb, 0, 0)

        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(2, 0)

        self.grid.setRowStretch(2, 1)

        self.vbox = QVBoxLayout()
        self.grid.addLayout(self.vbox, 0, 2, 2, 1)

        self.AHT_widget = QAHTWidget(self.config, self.ESP)
        self.vbox.addWidget(self.AHT_widget, 0)

        self.RLED_widget = QLEDControlWidget(self.config, self.ESP,
            name="RLD", label="Red LED")
        self.BLED_widget = QLEDControlWidget(self.config, self.ESP,
            name="BLD", label="Blue LED")
        self.vbox.addWidget(self.RLED_widget, 1)
        self.vbox.addWidget(self.BLED_widget, 2)

class TaskManager:

    def update_UI(self, command, arguments):
        pass