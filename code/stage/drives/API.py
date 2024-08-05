from backend import QResource

class QDrive(QResource):
	
	def __init__(self, resource):

		# Reinitialize base class resource
		self.name = resource.name
		self.master_int = resource.master_int
		self.config = resource.config

		super().__init__(self.name, self.master_int)
