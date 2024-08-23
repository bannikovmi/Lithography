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
		self.start_pos = self.drive.pos
		self.var = np.nan

	def run(self):

		self.signals.started.emit()

		# Set drive and camera settings
		self.set_drive_settings()
		self.set_cam_settings()
		
		self.signals.status_updated.emit("Configuring scan params")

		# Construct a grid
		start = self.scan_params["start"]
		stop = self.scan_params["stop"]
		step = self.scan_params["step"]

		# Create var and pos lists
		self.pos_list = []
		self.var_list = []

		# Go to start
		self.signals.status_updated.emit(f"Moving to shift={start}")
		self.drive.start_movement(start*self.drive.config["pos_direction"])
		self.wait_for_movement_end()
		self.update_lists()
 
		while self.drive.pos < self.start_pos + stop:
	
			self.signals.status_updated.emit(f"Moving to {float(self.drive.pos)}")
			self.drive.start_movement(step*self.drive.config["pos_direction"])
			self.wait_for_movement_end()
			self.update_lists()

		self.signals.status_updated.emit("Idle")
		self.signals.finished.emit()

	def update_lists(self):

		self.pos_list.append(float(self.drive.pos))
		self.var_list.append(self.var)
		self.signals.data_updated.emit(self.pos_list, self.var_list)

	def wait_for_movement_end(self):
		
		while self.drive.is_moving:
			time.sleep(self.scan_params["polling_interval"]*1e-3)

	def set_drive_settings(self):
		
		self.signals.status_updated.emit("Updating drive settings")
		# Ensure that the drive is enabled, set speed and microstep
		self.drive.set("power", 1)
		self.drive.set("speed", self.scan_params["drive"]["speed"])
		self.drive.set("mstep", self.scan_params["drive"]["mstep"])

	def set_cam_settings(self):

		self.signals.status_updated.emit("Updating camera settings")
		pass
