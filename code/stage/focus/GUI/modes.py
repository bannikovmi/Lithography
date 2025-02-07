from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QRadioButton
)

class DriveMode:

    SUBSTRATE = 0
    PROJECTOR = 1

class ScanMode:

    NONE = 0
    MANUAL = 1
    AUTO = 2

class QDriveModeGB(QGroupBox):

    mode_changed = pyqtSignal(int)

    def __init__(self):

        super().__init__("Drive mode")

        self.initUI()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.sub_rb = QRadioButton("Substrate")
        self.proj_rb = QRadioButton("Projector")

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.sub_rb, 0, 0)
        self.grid.addWidget(self.proj_rb, 0, 1)

    def connect_signals(self):

        self.sub_rb.clicked.connect(lambda:
            self.mode_changed.emit(DriveMode.SUBSTRATE))
        self.proj_rb.clicked.connect(lambda:
            self.mode_changed.emit(DriveMode.PROJECTOR))

    def set_default_values(self):

        self.sub_rb.setChecked(True)

class QScanModeGB(QGroupBox):

    mode_changed = pyqtSignal(int)

    def __init__(self):

        super().__init__("Scan mode")

        self.initUI()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.none_rb = QRadioButton("None")
        self.man_rb = QRadioButton("Manual")
        self.auto_rb = QRadioButton("Auto")

        self.auto_rb.setDisabled(True) # TEMPORARY

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.none_rb, 0, 0)
        self.grid.addWidget(self.man_rb, 0, 1)
        self.grid.addWidget(self.auto_rb, 0, 2)

    def connect_signals(self):

        self.none_rb.clicked.connect(lambda:
            self.mode_changed.emit(ScanMode.NONE))
        self.auto_rb.clicked.connect(lambda:
            self.mode_changed.emit(ScanMode.AUTO))
        self.man_rb.clicked.connect(lambda:
            self.mode_changed.emit(ScanMode.MANUAL))

    def set_default_values(self):

        self.none_rb.setChecked(True)
