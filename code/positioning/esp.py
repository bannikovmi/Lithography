# third-party imports
import pyvisa

# pyqt-related imports
from PyQt5.QtCore import QObject

class ESP(QObject):

    def __init__(self, config, simulation=False):

        super().__init__()

        self.config = config
        self.simulation = simulation

        # Open pyvisa session and configure the device
        self.rm = pyvisa.ResourceManager("@py")
        self.resource = self.rm.open_resource(
            self.config["Task_manager"]["pyvisa"]["address"])

        baud_rate = self.config["Task_manager"]["pyvisa"]["baud_rate"]
        read_termination = self.config["Task_manager"]["pyvisa"]["read_termination"]
        write_termination = self.config["Task_manager"]["pyvisa"]["write_termination"]
        timeout = self.config["Task_manager"]["pyvisa"]["timeout"]

        self.resource.baud_rate = baud_rate
        self.resource.read_termination = read_termination
        self.resource.write_termination = write_termination
        self.resource.timeout = timeout

    def write(self, message):
        self.resource.write(message)

    def read(self):
        return self.resource.read()

    def query(self, message):
        return self.resource.query(message)
