from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget
    )

from .params import QDriveParams
from .move_button import QMoveButton
from .numeric import QNumericIndicator

class QPlaneGB(QGroupBox):

    def __init__(self, config, esp):

        self.config = config
        self.esp = esp

        super().__init__("In-plane positioning")
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.x_params = QDriveParams(self.config, self.esp, name="DRX")
        self.y_params = QDriveParams(self.config, self.esp, name="DRY")
        self.positioner = QPositionerWidget(self.config, self.esp)

        self.grid.addWidget(self.y_params, 0, 0)
        self.grid.addWidget(self.x_params, 1, 0)
        self.grid.addWidget(self.positioner, 0, 1, 2, 1)

class QArrowButtonGroup(QWidget):

    def __init__(self, config, esp):

        self.config = config
        self.esp = esp

        super().__init__()
        self.initUI()

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.negx_pb = QMoveButton("left")
        self.posx_pb = QMoveButton("right")
        self.negy_pb = QMoveButton("down")
        self.posy_pb = QMoveButton("up")

        self.vbox.addStretch(1)
        self.vbox.addWidget(self.posy_pb, 0, alignment=Qt.AlignHCenter)
        
        self.hbox = QHBoxLayout()
        self.vbox.addLayout(self.hbox, 1)
        self.vbox.addStretch(1)

        self.hbox.addStretch(1)
        self.hbox.addWidget(self.negx_pb, 0)
        self.hbox.addWidget(self.negy_pb, 1)
        self.hbox.addWidget(self.posx_pb, 2)
        self.hbox.addStretch(1)

class QPositionerWidget(QGroupBox):

    def __init__(self, config, esp):

        self.config = config
        self.esp = esp

        super().__init__("Movement")
        self.initUI()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.arrow_button_group = QArrowButtonGroup(self.config, self.esp)
        self.grid.addWidget(self.arrow_button_group, 0, 0)
        self.x_indicator = QNumericIndicator(
            label="X pos",
            min_value=self.config["Drives"]["DRX"]["min_position"],
            max_value=self.config["Drives"]["DRX"]["max_position"],
            orientation=Qt.Horizontal
        )
        self.y_indicator = QNumericIndicator(
            label="Y pos",
            min_value=self.config["Drives"]["DRY"]["min_position"],
            max_value=self.config["Drives"]["DRY"]["max_position"],
            orientation=Qt.Vertical
        )
        self.grid.addWidget(self.x_indicator, 1, 0)
        self.grid.addWidget(self.y_indicator, 0, 1)
