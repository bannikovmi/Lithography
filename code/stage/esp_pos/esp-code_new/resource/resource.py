class Resource():

    available_commands = {
    }

    def exec_command(self, name, *args):
        getattr(self, self.available_commands[name])(*args)

    def update_config(self):
        self.esp.config[self.name] = self.config
        
    def dump_config(self, config_path=None):
        self.esp.dump_config(config_path)
