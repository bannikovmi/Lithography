class Resource():

	available_commands = {
	}

	def exec_command(self, name, *args):
		getattr(self, self.available_commands[name])(*args)

