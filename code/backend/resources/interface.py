# standart library imports
import json

# pyqt-related imports
from PyQt5.QtCore import QObject

class QInterface(QObject):

    slaves = {}
    config = {}

    def __init__(self, name, master):

        self.name = name
        self.master = master

        super().__init__()

    def add_slave(self, slave):
        self.slaves[slave.name] = slave
    
    def load_config(self, config_path):
        
        with open(config_path, "r") as file:    
            self.config = json.load(file)

    def dump_config(self, config_path):

        with open(config_path, 'w') as file:
            json.dump(self.config, file, indent=4)
