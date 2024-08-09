from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget
    )

from stage.drives.API.drive import QDrive
from widgets.numeric import QNumericIndicator

from .params import QDriveParams
from .move_button import QMoveButton


class QVerticalGB(QGroupBox):

    def __init__(self, config, resource_manager):

        # Save arguments to instance attributes
        self.config = config
        self.rm = resource_manager

        super().__init__("Vertical positioning")
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.params = QDriveParams(self.config["params"])
        self.positioner = QPositionerWidget(self.config["positioner"])
        
        self.grid.addWidget(self.positioner, 0, 0)
        self.grid.addWidget(self.params, 0, 1)

class QArrowButtonGroup(QWidget):

    def __init__(self, config):

        self.config = config

        super().__init__()
        self.initUI()

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.neg_pb = QMoveButton("down")
        self.pos_pb = QMoveButton("up")

        self.vbox.addStretch(1)
        self.vbox.addWidget(self.pos_pb, 0, alignment=Qt.AlignVCenter)
        self.vbox.addWidget(self.neg_pb, 1, alignment=Qt.AlignVCenter)
        self.vbox.addStretch(1)

class QPositionerWidget(QGroupBox):

    def __init__(self, config):

        self.config = config

        super().__init__("Movement")
        self.initUI()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.hbox.addStretch(1)
        self.arrow_button_group = QArrowButtonGroup(self.config)
        self.hbox.addWidget(self.arrow_button_group, 0)
        self.hbox.addStretch(1)

        # self.indicator = QNumericIndicator(
        #     label="Z pos",
        #     min_value=self.config["Drives"]["DRZ"]["min_position"],
        #     max_value=self.config["Drives"]["DRZ"]["max_position"],
        #     orientation=Qt.Vertical
        # )
        # self.hbox.addWidget(self.indicator, 1)
