from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QGridLayout,
	QGroupBox,
	QHBoxLayout,
	QVBoxLayout,
	QWidget,
	)

from .move_button import QMoveButton
from .numeric import QNumericIndicator
from .params import QDriveParams


class QLenseGB(QGroupBox):

	def __init__(self, config, esp):

		self.config = config
		self.esp = esp

		super().__init__("Lense positioning")
		self.initUI()

	def initUI(self):

		self.grid = QGridLayout()
		self.setLayout(self.grid)

		self.params = QDriveParams(self.config, self.esp, name="DRL")
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

        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.neg_pb = QMoveButton("left")
        self.pos_pb = QMoveButton("right")

        self.hbox.addStretch(1)
        self.hbox.addWidget(self.neg_pb, 0, alignment=Qt.AlignVCenter)
        self.hbox.addWidget(self.pos_pb, 1, alignment=Qt.AlignVCenter)
        self.hbox.addStretch(1)

class QPositionerWidget(QGroupBox):

    def __init__(self, config, esp):

        self.config = config
        self.esp = esp

        super().__init__()
        self.initUI()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.vbox.addStretch(1)
        self.arrow_button_group = QArrowButtonGroup(self.config, self.esp)
        self.vbox.addWidget(self.arrow_button_group, 0)
        self.vbox.addStretch(1)

        self.indicator = QNumericIndicator(
            label="Lense pos",
            min_value=self.config["Drives"]["DRL"]["min_position"],
            max_value=self.config["Drives"]["DRL"]["max_position"],
            orientation=Qt.Horizontal
        )
        self.vbox.addWidget(self.indicator, 1)
