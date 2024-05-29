#!/usr/bin/python

"""
Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QWidget

# local imports
from .vacuum import QVacuumWidget
from .plane import QPlanePositioningWidget
from .height import QZMotionWidget
from .lense import QLenseMotionWidget

class QPositioningTab(QWidget):

    def __init__(self, config, ESP):
        
        self.config = config
        self.ESP = ESP

        super().__init__()
        self.initUI()
        self.connect_signals()

    def initUI(self):
    
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # self.vacuum_widget = QVacuumWidget(self.config, self.ESP)
        # self.grid.addWidget(self.vacuum_widget, 0, 0)

        self.z_motion_widget = QZMotionWidget(self.config, self.ESP)
        self.grid.addWidget(self.z_motion_widget, 1, 0)

        self.lense_motion_widget = QLenseMotionWidget(self.config, self.ESP)
        self.grid.addWidget(self.lense_motion_widget, 0, 1)

        self.plane_positioning_widget = QPlanePositioningWidget(self.config, self.ESP)
        self.grid.addWidget(self.plane_positioning_widget, 1, 1)


    def connect_signals(self):

        pass
        # self.vacuum_widget.state_changed.connect(self.plane_positioning_widget.setEnabled)

        # self.grid.setColumnStretch(2, 1)

    # def on_timer_event(self):

    #     self.temp_monitor_widget.on_timer_event()
    #     self.temp_control_widget.on_timer_event()
