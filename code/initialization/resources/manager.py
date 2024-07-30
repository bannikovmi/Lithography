# standart library imports
import os

# third-party imports
# pyqt-related imports
from PyQt5.QtCore import QObject

import pyvisa

# local imports
from interface import QInterface
from resource import QResource

class QResourceManager(QObject):

    resources = {}

    def __init__(self, config):

        self.config = config
        self.pyvisa_rm = pyvisa.ResourceManager("@py")

        super().__init__()

        rasp4 = QResource(name="rasp4") # Host resource
        
        self.resources["rasp4"] = rasp4
        dir_path = os.path.join("..", "..", "config", "resources")
        rasp4.load_config(os.path.join(dir_path), "resource.json")

        for name in os.listdir(dir_path):
            new_path = os.path.join(dir_path, name)
            self.(dir_path)

    def add_resource(self, dir_path):

        for name in os.listdir(dir_path):

            new_path = os.path.join(dir_path, name)

            if not os.path.isdir(new_path):
                self.resources[]

    def add_interface(self, dir_path):

        pass

    # def dir_scan(dir_name):
    #     """
    #     Perform recursive scan of directories for files with .json extension,
    #     initialize resources and add them to dictionary.
    #     """

    #     ret = {}

    #     for name in os.listdir(dir_name):

    #         new_path = os.path.join(dir_name, name)
    #         if os.path.isdir(new_path):
    #             ret[name] = dir_scan(new_path)
    #         else:
    #             with open(new_path, "r") as file:
    #                 ret[name.split('.')[0]] = json.load(file)

    #     return ret

    # # def add_interface(self, int_name, int_value, parent=None):

    # #     interface = QInterface(int_name)

    # #     for key, val in int_value.items():

    # #         if not isinstance(val, dict): # interface params are not dictionaries
    # #             print("setting attribute to interface", int_name, key, val)
    # #             setattr(interface, key, val) # add custom data to interface
    # #         else: 
    # #             pyvisa_handler = None
    # #             try:
    # #                 pyvisa_address = val["pyvisa_address"]
    # #                 pyvisa_handler = self.pyvisa_rm.open_resource(pyvisa_address)
    # #             except KeyError: # resource has no pyvisa address
    # #                 pass

    # #             resource = QResource(key, pyvisa_handler,
    # #                 parent=parent, interface=int_name)
    # #             self.resources[key] = resource

    # #             # iterate over values in resource dictionary interfaces
    # #             for name, value in val.items():
    # #                 if not isinstance(value, dict):
    # #                     setattr(resource, name, value) # add custom data to resource
    # #                 else:
    # #                     self.add_interface(name, value, parent=resource)