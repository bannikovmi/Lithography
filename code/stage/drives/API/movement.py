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

		old_timeout = self.drive.esp.pyvisa_handler.timeout
		new_timeout = int(2000+1.2e3*abs(self.nsteps)/self.drive._speed)
		self.drive.esp.pyvisa_handler.timeout = new_timeout
		print(f"timeouts: old={old_timeout:.2f}, new={new_timeout:.2f}")

		self.drive.launch_movement(self.nsteps)

		while self.drive.is_moving:
			
			self.drive.is_moving = not self.drive.check_finish()

		self.drive.update_status()
		time.sleep(100e-3)
		self.drive.esp.pyvisa_handler.timeout = old_timeout

		self.signals.finished.emit()
