# standart library imports
import json

# pyqt-related imports
from PyQt5.QtCore import QMutex, QObject, QThreadPool

class QResource(QObject):

    def __init__(self, arg1, master_int=None):

        if isinstance(arg1, QResource):
            # Copy data from resource to instance attributes
            self.copy_resource(arg1)
        else:
            # Save data to instance attributes
            self.name = arg1
            self.master_int = master_int

            # Create dictionaries for storing config and slave interfaces
            self.interfaces = {}
            self.config = {}
            
            # Global thread pool instance
            self.thread_pool = QThreadPool.globalInstance()

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

    def copy_resource(self, resource):
        
        self.name = resource.name
        self.master_int = resource.master_int
        self.config = resource.config
        self.interfaces = resource.interfaces
        self.thread_pool = resource.thread_pool
