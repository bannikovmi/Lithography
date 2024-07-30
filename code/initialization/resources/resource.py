# standart library imports
import json

# pyqt-related imports
from PyQt5.QtCore import QMutex, QObject

class QResource(QObject):

    interfaces = {}
    config = {}

    def __init__(self, 
        name: str = "",
        master_interface=None,
    ):

        # Save data to local variables
        self.name = name
        self.master_interface = master_interface

        super().__init__()

    def load_config(self, config_path):
        
        with open(config_path, "r") as file:    
            self.config = json.load(file)

    def dump_config(self, config_path):

        with open(config_path, 'w') as file:
            json.dump(self.config, file, indent=4)

    def add_interface(self, interface):
        self.interfaces[interface.name] = interface

    @property
    def master(self):
        # get master device
        return self.master_interface.master

    @property
    def slaves(self):
        # get all slaves for all interfaces in form of a dict
        ret = {}
        for int_name, interface in self.interfaces:
            ret[int_name] = interface.slaves
        return ret

class QVISAResource(QResource):

    def __init__(self,
        name: str="",
        parent_int=None,
        pyvisa_handler=None,
    ):

        super().__init__(name, parent_int)
        self.pyvisa_handler = pyvisa_handler

    # Common methods
    def clear(self):
        self.pyvisa_handler.clear()

    def open(self):
        self.pyvisa_handler.open()

    def close(self):
        self.pyvisa_handler.close()

    def read(self):
        return self.pyvisa_handler.read()

    def write(self, message):

        return self.pyvisa_handler.write(message)

    def query(self, message):
        
        return self.pyvisa_handler.query(message)

    # Mutex version of query
    def mutex_query(self, message):
        
        self.mutex.lock()
        res = self.query(message)
        self.mutex.unlock()

        return res
