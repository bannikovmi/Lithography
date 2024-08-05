from PyQt5.QtCore import pyqtSignal, QObject

class QTaskManager(QObject):

	def __init__(self, config, resource_manager):
		
		self.config = config
		self.resource_manager = resource_manager
		
		super().__init__()

