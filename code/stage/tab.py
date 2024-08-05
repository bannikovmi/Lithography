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
from .camera.gui import QCameraWidget
from .drives.gui.plane import QPlaneGB
from .drives.gui.vertical import QVerticalGB
from .drives.gui.lense import QLenseGB
# from .misc.climate import QAHTWidget
# from .misc.LED import QBasicLEDWidget
# from .misc.vacuum import QVacuumWidget

class QStageTab(QWidget):

    widgets = {}

    def __init__(self, task_manager, simulation=False):

        super().__init__()

        self.task_manager = task_manager
        self.simulation = simulation

        self.initUI()
        # self.task_manager.message_received.connect(self.updateUI)
        # self.task_manager.timer.start()

    def initUI(self):
    
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.plane_gb = QPlaneGB(self.task_manager)
        # self.vertical_gb = QVerticalGB(self.config)
        # self.lense_gb = QLenseGB(self.config)

        # self.grid.addWidget(self.lense_gb, 0, 1)
        # self.grid.addWidget(self.vertical_gb, 1, 1)
        self.grid.addWidget(self.plane_gb, 2, 1)

        # self.grid.setRowStretch(0, 1)
        # self.grid.setRowStretch(1, 1)
        # self.grid.setRowStretch(2, 1)

        # self.vbox = QVBoxLayout()
        # self.grid.addLayout(self.vbox, 0, 0, 3, 1)

        # self.camera_widget = QCameraWidget(self.config)
        # self.vbox.addWidget(self.camera_widget, 0)

        # self.hbox = QHBoxLayout()
        # self.vbox.addLayout(self.hbox, 1)

        # self.aht_widget = QAHTWidget(self.config)
        # self.illumination_widget = QBasicLEDWidget(self.config, name="RLD")
        # self.hbox.addWidget(self.illumination_widget, 0)
        # self.hbox.addWidget(self.aht_widget, 1)

        # self.hbox.setStretch(0, 0)
        # self.hbox.setStretch(1, 0)
        # self.hbox.addStretch(1)

        # self.grid.setColumnStretch(0, 1)
        # self.grid.setColumnStretch(1, 0)

        # Add widgets to dictionary according by resource names
        # Different resources may be associated with the same widget
        # self.widgets["DRX"] = self.plane_gb
        # self.widgets["DRY"] = self.plane_gb
        # self.widgets["DRZ"] = self.vertical_gb
        # self.widgets["DRL"] = self.lense_gb
        # self.widgets["CAM"] = self.camera_widget
        # self.widgets["AHT"] = self.aht_widget
        # self.widgets["RLD"] = self.illumination_widget

    def updateUI(self, message):
        
        try:
            self.widgets[message.resource_name].updateUI(message)
        except AttributeError:
            pass

        # self.vergical_gb = QVerticalGB(self.config, self.esp)
        # self.lense_gb = QLenseGB(self.config, self.esp)

#         self.lense_motion_gb = QMotionGB(self.config, self.ESP, name="DRL")
#         self.x_motion_gb = QMotionGB(self.config, self.ESP, name="DRX")
#         self.y_motion_gb = QMotionGB(self.config, self.ESP, name="DRY")
#         self.z_motion_gb = QMotionGB(self.config, self.ESP, name="DRZ")

#         self.grid.addWidget(self.x_motion_gb, 1, 1)
#         self.grid.addWidget(self.y_motion_gb, 1, 0)
#         self.grid.addWidget(self.lense_motion_gb, 0, 1)
#         self.grid.addWidget(self.z_motion_gb, 0, 0)

#         # self.grid.setColumnStretch(0, 1)
#         # self.grid.setColumnStretch(1, 1)
#         # self.grid.setColumnStretch(2, 0)

#         # self.grid.setRowStretch(2, 1)

#         # self.vbox = QVBoxLayout()
#         # self.grid.addLayout(self.vbox, 0, 2, 2, 1)

#         # self.AHT_widget = QAHTWidget(self.config, self.ESP)
#         # self.vbox.addWidget(self.AHT_widget, 0)

#         # self.RLED_widget = QLEDControlWidget(self.config, self.ESP,
#         #     name="RLD", label="Red LED")
#         # self.BLED_widget = QLEDControlWidget(self.config, self.ESP,
#         #     name="BLD", label="Blue LED")
#         # self.vbox.addWidget(self.RLED_widget, 1)
#         # self.vbox.addWidget(self.BLED_widget, 2)
