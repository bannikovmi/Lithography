from PyQt5.QtCore import QObject

class QTaskManager(QObject):

	def __init__(self, config):
		
		self.config = config
		super().__init__()