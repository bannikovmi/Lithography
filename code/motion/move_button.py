from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QShortcut, QToolButton

class QMoveButton(QToolButton):

	directions = {
		"down": (Qt.DownArrow, QKeySequence(Qt.Key_Down)),
		"left": (Qt.LeftArrow, QKeySequence(Qt.Key_Left)),
		"right": (Qt.RightArrow, QKeySequence(Qt.Key_Right)),
		"up": (Qt.UpArrow, QKeySequence(Qt.Key_Up))
	}

	def __init__(self, direction):

		super().__init__()
		
		self.setArrowType(self.directions[direction][0])
		self.setShortcut(self.directions[direction][1])
		self.setAutoRepeat(True)
		self.setAutoRepeatDelay(100)

	def on_single_press(self):

		self.esp
