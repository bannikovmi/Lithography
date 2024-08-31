import time

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
		
		self.drive.launch_movement(self.nsteps)
		self.drive.is_moving = True

		while self.drive.is_moving:
			
			at_min, at_max, pos, self.drive.is_moving = self.drive.get_status()
			self.signals.min_checked.emit(at_min)
			self.signals.max_checked.emit(at_max)
			self.signals.pos_updated.emit(pos)

			# Allow other threads to work and get some time between communications
			time.sleep(30e-3) 

		self.signals.finished.emit()
