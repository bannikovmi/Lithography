class Command():

	def __init__(self, message=""):

		split_message = message.split("_")
		self.resource_name = split_message[0]
		self.name = split_message[1]
		self.args = split_message[2:]
