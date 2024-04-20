#!/usr/bin/python

"""
Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QWidget

# local imports
from .plane import QPlaneMotionWidget

class QMotionTab(QWidget):

    def __init__(self, config, ESP):
        
        self.config = config
        self.ESP = ESP

        super().__init__()
        self.initUI()

    def initUI(self):
    
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.plane_motion_widget = QPlaneMotionWidget(self.config, self.ESP)
        self.grid.addWidget(self.plane_motion_widget, 0, 0)

        self.grid.setColumnStretch(1, 1)

    # def on_timer_event(self):

    #     self.temp_monitor_widget.on_timer_event()
    #     self.temp_control_widget.on_timer_event()
