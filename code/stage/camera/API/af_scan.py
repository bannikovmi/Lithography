import time
import numpy as np

from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, QThreadPool

class RunnerSignals(QObject):

	started = pyqtSignal()
	finished = pyqtSignal()
	status_updated = pyqtSignal(str)
	data_updated = pyqtSignal(list, list)

class QScanRunner(QRunnable):

	def __init__(self, drive, scan_params):
		
		super().__init__()

		self.drive = drive
		self.scan_params = scan_params
		
		self.signals = RunnerSignals()
		
		# Initial values for position and variance
		self.drive.update_status()
		self.start_pos = self.drive.pos
		self.var = np.nan

	def run(self):

		self.signals.started.emit()

		# Set drive and camera settings
		self.set_drive_settings()
		self.set_cam_settings()

		# Construct a grid
		start = self.scan_params["start"]
		stop = self.scan_params["stop"]
		step = self.scan_params["step"]

		# Create var and pos lists
		self.pos_list = []
		self.var_list = []

		# Go to start
		self.signals.status_updated.emit(f"Moving to {float(self.drive.pos)+start}")
		self.drive.move_nsteps(start)
		self.update()

		current_pos = self.start_pos + start
 
		while current_pos + step <= self.start_pos + stop:

			self.signals.status_updated.emit(f"Moving to {float(self.drive.pos)+step}")
			self.drive.move_nsteps(step)
			current_pos += step
			self.update()
			print(f"{self.start_pos + start} < {current_pos},{self.drive.pos} < {self.start_pos + stop}")

		self.signals.status_updated.emit("Idle")
		self.signals.finished.emit()

	def update(self):

		# wait for movement end
		while self.drive.is_moving:
			time.sleep(200e-3)

		self.pos_list.append(float(self.drive.pos))
		self.var_list.append(self.var)
		self.signals.data_updated.emit(self.pos_list, self.var_list)
			

	def set_drive_settings(self):
		
		self.signals.status_updated.emit("Updating drive settings")
		# Ensure that the drive is enabled, set speed and microstep
		self.drive.set("power", 1)
		self.drive.set("speed", self.scan_params["drive"]["speed"])
		self.drive.set("mstep", self.scan_params["drive"]["mstep"])

	def set_cam_settings(self):

		self.signals.status_updated.emit("Updating camera settings")
