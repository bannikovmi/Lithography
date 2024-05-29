# standard library imports
import sys, os

# pyqt-related imports
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QCheckBox, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QRadioButton, QSpinBox)
import pyqtgraph as pg

# local imports
sys.path.insert(0, os.path.abspath('..')) # enable import from sibling packages
from gui.numeric import QNumericControl

from .move_button import QMoveButton

class QLenseMotionWidget(QGroupBox):

    def __init__(self, config, ESP, label="Lense motion"):

        super().__init__(label)
        self.config = config
        self.ESP = ESP
        self.initUI()

    def initUI(self):
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.arrow_button_group = QLenseArrowButtonGroup(self.config)
        self.grid.addWidget(self.arrow_button_group, 0, 0)

        self.mode_gb = QGroupBox("Mode")
        self.mode_grid = QGridLayout()
        self.mode_gb.setLayout(self.mode_grid)

        self.single_rb = QRadioButton("single-step")
        self.continious_rb = QRadioButton("continious")
        self.mode_grid.addWidget(self.single_rb, 0, 0)
        self.mode_grid.addWidget(self.continious_rb, 1, 0)

        self.single_rb.clicked.connect(self.toggle_mode)
        self.continious_rb.clicked.connect(self.toggle_mode)

        self.grid.addWidget(self.mode_gb, 1, 0)

        self.speed_control = QNumericControl(label="Speed", units="μm/s",
            mapper_type="linear", orientation=Qt.Horizontal)
        self.speed_control.setMinimum(0.1)
        self.speed_control.setMapper("log10")
        self.grid.addWidget(self.speed_control, 0, 1)

        self.step_control = QNumericControl(label="Step", units="μm",
            mapper_type="linear", orientation=Qt.Horizontal)
        self.step_control.setMinimum(0.1)
        self.step_control.setMaximum(10000)
        self.step_control.setMapper("log10")
        self.grid.addWidget(self.step_control, 1, 1)

        self.continious_rb.setChecked(True)
        self.step_control.setDisabled(True)
        self.toggle_mode()

    def toggle_mode(self):

        if self.continious_rb.isChecked():
            self.speed_control.setDisabled(False)
            self.step_control.setDisabled(True)
            self.arrow_button_group.setMode("continious")
        else:
            self.speed_control.setDisabled(True)
            self.step_control.setDisabled(False)
            self.arrow_button_group.setMode("single")

class QLenseArrowButtonGroup(QGroupBox):

    def __init__(self, config, label=None):

        self.config = config
        self.mode = "continious"

        super().__init__(label)
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.left_pb = QMoveButton("left")
        self.right_pb = QMoveButton("right")

        self.grid.addWidget(self.left_pb, 0, 0)
        self.grid.addWidget(self.right_pb, 0, 1)

        # self.down_led = QRoundLedIndicator()
        # self.left_led = QRoundLedIndicator()
        # self.right_led = QRoundLedIndicator()
        # self.up_led = QRoundLedIndicator()

        # self.grid.addWidget(self.down_led, 3, 2)
        # self.grid.addWidget(self.left_led, 2, 0)
        # self.grid.addWidget(self.right_led, 2, 4)
        # self.grid.addWidget(self.up_led, 0, 2)

    def setMode(self, mode):

        match mode:
            case "continious":
                self.left_pb.setAutoRepeat(True)
                self.right_pb.setAutoRepeat(True)
            case "single":
                self.left_pb.setAutoRepeat(False)
                self.right_pb.setAutoRepeat(False)
            case _:
                raise ValueError("Unknown mode")
