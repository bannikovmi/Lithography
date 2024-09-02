import time

from PyQt5.QtCore import pyqtSignal, QObject, QRunnable

from stage.drives.API.position import DrivePosition

class RunnerSignals(QObject):

	started = pyqtSignal()
	finished = pyqtSignal()

class MovementRunner(QRunnable):

	def __init__(self, drive, nsteps):

		super().__init__()

		self.drive = drive
		self.nsteps = nsteps

		self.signals = RunnerSignals()

	def run(self):

		self.signals.started.emit()
		self.drive.launch_movement(self.nsteps)

		while self.drive.is_moving:
			
			self.drive.update_status()

			# Allow other threads to work and get some time between communications
			time.sleep(30e-3) 

		self.signals.finished.emit()
		print("movement: finished")
