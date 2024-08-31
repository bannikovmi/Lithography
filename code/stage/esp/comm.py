import time

from PyQt5.QtCore import pyqtSignal, QObject, QRunnable

class RunnerSignals(QObject):

	message_received = pyqtSignal(str)

class ESPCommRunner(QRunnable):

	def __init__(self, handler):

		super().__init__()

		self.handler = handler
		self.signals = RunnerSignals()
		self.is_finished = False

	def run(self):

		while not self.is_finished:
			# Sleep for some time so other threads may work
			time.sleep(10e-3)

	def write(self, message):
		self.handler.write(message)
		self.handler.read() # skip echo

	def read(self):
		message = self.handler.read()
		self.signals.message_received.emit(message)
		return message
	
	def query(self, message):
		self.write(message)
		return self.read()
