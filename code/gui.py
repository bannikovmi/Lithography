# pyqt-related imports
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QCheckBox, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QRadioButton, QSpinBox)
import pyqtgraph as pg

# local imports
from led import QLedIndicator

class QMotionStepperWidget(QGroupBox):

    def __init__(self, config, label="Motion control"):

        super().__init__(label)
        self.config = config
        self.initUI()

    def initUI(self):
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.clockwise_rb = QRadioButton("Clockwise")
        self.counterclockwise_rb = QRadioButton("Counterclockwise")
        self.clockwise_rb.setChecked(True)

        self.nsteps_label = QLabel("Steps")
        self.nsteps_sb = QSpinBox()
        self.nsteps_sb.setRange(1, 100)r
        self.execute_pb = QPushButton("Execute")

        self.clockwise_lim_lab = QLabel("Clockwise max")
        self.counterclockwise_lim_lab = QLabel("Counterclockwise max")
        self.clockwise_lim_led = QLedIndicator()
        self.counterclockwise_lim_led = QLedIndicator()

        self.clockwise_lim_led.setDisabled(True)
        self.counterclockwise_lim_led.setDisabled(True)

        self.grid.addWidget(self.clockwise_rb, 0, 0)
        self.grid.addWidget(self.counterclockwise_rb, 1, 0)

        self.grid.addWidget(self.nsteps_label, 0, 1)
        self.grid.addWidget(self.nsteps_sb, 0, 2)

        self.grid.addWidget(self.execute_pb, 1, 1, 1, 2)

        self.grid.addWidget(self.clockwise_lim_lab, 0, 3)
        self.grid.addWidget(self.counterclockwise_lim_lab, 1, 3)
        self.grid.addWidget(self.clockwise_lim_led, 0, 4)
        self.grid.addWidget(self.counterclockwise_lim_led, 1, 4)
