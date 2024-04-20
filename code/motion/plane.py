# standard library imports
import sys, os

# pyqt-related imports
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QCheckBox, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QRadioButton, QShortcut, QSpinBox)
import pyqtgraph as pg

# local imports
sys.path.insert(0, os.path.abspath('..')) # enable import from sibling packages
from gui.led import QLedIndicator

from .move_button import QMoveButton

class QPlaneMotionWidget(QGroupBox):

    def __init__(self, config, ESP, label="XY motion"):

        self.config = config
        self.ESP = ESP

        super().__init__(label)
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.arrow_button_group = QArrowButtonGroup(self.config, self.ESP)
        self.grid.addWidget(self.arrow_button_group, 0, 0, 2, 1)

        self.single_rb = QRadioButton("single")
        self.continious_rb = QRadioButton("continious")
        self.single_rb.setChecked(True)

        self.grid.addWidget(self.single_rb, 0, 1)
        self.grid.addWidget(self.continious_rb, 1, 1)

        # self.down_pb.pressed.connect(self.move_down)
        # self.left_pb.clicked.connect(self.move_left)
        # self.right_pb.clicked.connect(self.move_right)
        # self.up_pb.clicked.connect(self.move_up)

    # def move_down(self):

    #     if self.single_rb.isChecked():
    #         self.

        # self.clockwise_rb = QRadioButton("Clockwise")
        # self.counterclockwise_rb = QRadioButton("Counterclockwise")

        # self.nsteps_label = QLabel("Steps")
        # self.nsteps_sb = QSpinBox()
        # self.nsteps_sb.setRange(1, 100_000)
        # self.execute_pb = QPushButton("Execute")

        # self.clockwise_lim_lab = QLabel("Clockwise max")
        # self.counterclockwise_lim_lab = QLabel("Counterclockwise max")
        # self.clockwise_lim_led = QLedIndicator()
        # self.counterclockwise_lim_led = QLedIndicator()

        # self.clockwise_lim_led.setDisabled(True)
        # self.counterclockwise_lim_led.setDisabled(True)

        # self.grid.addWidget(self.clockwise_rb, 0, 0)
        # self.grid.addWidget(self.counterclockwise_rb, 1, 0)

        # self.grid.addWidget(self.nsteps_label, 0, 1)
        # self.grid.addWidget(self.nsteps_sb, 0, 2)

        # self.grid.addWidget(self.execute_pb, 1, 1, 1, 2)

        # self.grid.addWidget(self.clockwise_lim_lab, 0, 3)
        # self.grid.addWidget(self.counterclockwise_lim_lab, 1, 3)
        # self.grid.addWidget(self.clockwise_lim_led, 0, 4)
        # self.grid.addWidget(self.counterclockwise_lim_led, 1, 4)

class QArrowButtonGroup(QGroupBox):

    def __init__(self, config, ESP, label=None):

        self.config = config
        self.ESP = ESP

        super().__init__(label)
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.down_pb = QMoveButton("down")
        self.left_pb = QMoveButton("left")
        self.right_pb = QMoveButton("right")
        self.up_pb = QMoveButton("up")

        self.grid.addWidget(self.down_pb, 1, 1)
        self.grid.addWidget(self.left_pb, 1, 0)
        self.grid.addWidget(self.right_pb, 1, 2)
        self.grid.addWidget(self.up_pb, 0, 1)

