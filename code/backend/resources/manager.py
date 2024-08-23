# standart library imports
import os

# third-party imports
# pyqt-related imports
from PyQt5.QtCore import QObject

import pyvisa

# local imports
from .interface import QInterface
from .resource import QResource

class QResourceManager(QObject):

    resources = {}
    interfaces = {}

    def __init__(self, config):

        self.config = config
        self.pyvisa_rm = pyvisa.ResourceManager("@py")

        super().__init__()

        # Directory with resources
        dir_path = os.path.join("config", "resources", "host")

        # Add host resource, other interfaces and resources recursively
        self.add_resource(dir_path=dir_path, master_int=None)

    def __getitem__(self, key):
        return self.resources[key]

    def __setitem__(self, key, value):
        self.resources[key] = value

    def __delitem__(self, key):
        del self.resources[key]

    def add_resource(self, dir_path, master_int):

        # Create resource and load config
        res_name = os.path.basename(os.path.normpath(dir_path))
        config_path = os.path.join(dir_path, "resource.json")
        resource = QResource(res_name, config_path, master_int)
        resource.load_config()

        # Add resource to interfaces' slave dictionary and to self dictionary
        if master_int is not None:
            master_int.add_slave(resource)
            self.resources[res_name] = resource

        # Add slave interfaces recursively
        for name in os.listdir(dir_path):
            new_path = os.path.join(dir_path, name)
            if os.path.isdir(new_path):
                self.add_interface(dir_path=new_path, master=resource)

    def update_resource(self, key, new_class):

        old_resource = self[key]
        new_resource = new_class(self[key])

        # Update slave interfaces
        for interface in old_resource.interfaces.values():
            interface.master = new_resource
        # Update master interface
        old_resource.master_int.slaves[key] = new_resource

        # Update resource manager
        self[key] = new_resource

    def add_interface(self, dir_path, master):

        # Create interface and load config
        int_name = os.path.basename(os.path.normpath(dir_path))
        config_path = os.path.join(dir_path, "interface.json")
        interface = QInterface(int_name, config_path, master)
        interface.load_config()

        # Add interface to masters' interfaces dictionary and to self dictionary
        master.add_interface(interface)
        key = dir_path.removeprefix(os.path.join("config", "resources"))
        self.interfaces[key] = interface

        # Add slave resources recursively
        for name in os.listdir(dir_path):
            new_path = os.path.join(dir_path, name)
            if os.path.isdir(new_path):
                self.add_resource(dir_path=new_path, master_int=interface)
