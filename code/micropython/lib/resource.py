class Resource():

	available_commands = {
		"MS": "send_message"
	}

	def exec_command(self, name, *args):
		getattr(self, self.available_commands[name])(*args)

	def send_message(self, message):
		print(message)
		