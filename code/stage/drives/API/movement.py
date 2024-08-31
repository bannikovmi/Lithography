from PyQt5.QtCore import pyqtSignal, QObject, QRunnable

from stage.drives.API.position import DrivePosition

class RunnerSignals(QObject):

	started = pyqtSignal()
	finished = pyqtSignal()
	pos_updated = pyqtSignal(DrivePosition)

class MovementRunner(QRunnable):

	def __init__(self, drive, nsteps):

		self.drive = drive
		self.nsteps = nsteps

		self.signals = RunnerSignals()

	def run(self):

		self.signals.started.emit()
		self.signals.finished.emit()