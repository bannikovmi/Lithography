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

class QVerticalGB(QGroupBox):

	def __init__(self, config, esp):

		self.config = config
		self.esp = esp

		super().__init__("Vertical positioning")
		self.initUI()

	def initUI(self):

		self.grid = QGridLayout()
		self.setLayout(self.grid)

		self.params = QDriveParams(self.config, self.esp, name="DRZ")
		self.positioner = QPositionerWidget(self.config, self.esp)
		
		self.grid.addWidget(self.params, 0, 0)
		self.grid.addWidget(self.positioner, 0, 1)

class QArrowButtonGroup(QWidget):

    def __init__(self, config, esp):

        self.config = config
        self.esp = esp

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

    def __init__(self, config, esp):

        self.config = config
        self.esp = esp

        super().__init__("Movement")
        self.initUI()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.hbox.addStretch(1)
        self.arrow_button_group = QArrowButtonGroup(self.config, self.esp)
        self.hbox.addWidget(self.arrow_button_group, 0)
        self.hbox.addStretch(1)

        self.indicator = QNumericIndicator(
            label="Z pos",
            min_value=self.config["Drives"]["DRZ"]["min_position"],
            max_value=self.config["Drives"]["DRZ"]["max_position"],
            orientation=Qt.Vertical
        )
        self.hbox.addWidget(self.indicator, 1)
