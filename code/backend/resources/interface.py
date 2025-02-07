# standart library imports
import json

# pyqt-related imports
from PyQt5.QtCore import QObject

class QInterface(QObject):

    slaves = {}
    config = {}

    def __init__(self, name, config_path=None, master=None):

        # Save data to instance attributes
        self.name = name
        self.config_path = config_path
        self.master = master

        # Create dictionaries for storing config and slave resources
        self.slaves = {}
        self.config = {}

        super().__init__()

    def add_slave(self, slave):
        self.slaves[slave.name] = slave
    
    def load_config(self):
        
        with open(self.config_path, "r") as file:    
            self.config = json.load(file)

    def dump_config(self):

        with open(self.config_path, 'w') as file:
            json.dump(self.config, file, indent=4)
