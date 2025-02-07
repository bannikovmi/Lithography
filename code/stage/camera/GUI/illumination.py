# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, QTimer, QTime
from PyQt5.QtWidgets import (
    QGroupBox,
    QLabel,
    QLineEdit,
    QGridLayout,
    QPushButton,
    QRadioButton,
    QSpinBox,
    )

from stage.camera.API.illumination import QIlluminator

class QIlluminationGB(QGroupBox):

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager

        self.illuminator = QIlluminator(self.rm["RLD"])

        super().__init__("Illumination")
    
        self.initUI()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):
        
        self.setStyleSheet("background-color: white;")

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # Frequency
        self.freq_lab = QLabel("Frequency [Hz]")
        self.freq_sb = QSpinBox()
        self.freq_pb = QPushButton("Set")
        
        self.freq_sb.setMinimum(self.config["freq"]["min"])
        self.freq_sb.setMaximum(self.config["freq"]["max"])
        self.freq_sb.setSingleStep(self.config["freq"]["step"])

        # self.grid.addWidget(self.freq_lab, 0, 0)
        # self.grid.addWidget(self.freq_sb, 1, 0)
        # self.grid.addWidget(self.freq_pb, 2, 0)
        
        # Duty
        self.duty_lab = QLabel("Duty")
        self.duty_sb = QSpinBox()
        self.duty_pb = QPushButton("Set")
        
        self.duty_sb.setMinimum(self.config["duty"]["min"])
        self.duty_sb.setMaximum(self.config["duty"]["max"])
        self.duty_sb.setSingleStep(self.config["duty"]["step"])
        
        # self.grid.addWidget(self.duty_lab, 3, 0)
        self.grid.addWidget(self.duty_sb, 0, 0)
        self.grid.addWidget(self.duty_pb, 1, 0)

    def connect_signals(self):

        self.freq_pb.clicked.connect(self.set_freq)
        self.duty_pb.clicked.connect(self.set_duty)
        self.freq_sb.valueChanged.connect(lambda: self.freq_pb.setDisabled(False))
        self.duty_sb.valueChanged.connect(lambda: self.duty_pb.setDisabled(False))

    def set_default_values(self):

        self.freq_sb.setValue(self.config["freq"]["default"])
        self.duty_sb.setValue(self.config["duty"]["default"])
        self.set_freq()
        self.set_duty()

    def set_freq(self):

        self.freq_pb.setDisabled(True)
        value = self.freq_sb.value()
        self.illuminator.set("freq", value)

    def set_duty(self):

        self.duty_pb.setDisabled(True)
        value = self.duty_sb.value()
        self.illuminator.set("duty", value)
