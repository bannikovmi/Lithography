import json

class Resource():

    available_commands = {
    }

    def __init__(self, name):
        self.name = name
        self.config_path = f"config//{self.name}.json"
        self.load_config()

    def exec_command(self, name, *args):
        getattr(self, self.available_commands[name])(*args)
        
    def load_config(self):
        with open(self.config_path, "r") as file:
            self.config = json.load(file)
        
    def dump_config(self):
        with open(self.config_path, 'w') as file:
            json.dump(self.config, file)
