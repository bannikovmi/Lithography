# standart library imports
import time

# third-party imports
import pyvisa

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, QTimer

# local imports
from backend.resources.resource import QResource
from backend.resources.manager import ExecutionMode

class QESPPosMessage:

    def __init__(self, message=""):

        split_message = message.split("_")
        self.resource_name = split_message[0]
        self.command = split_message[1]
        self.arguments = split_message[2:]

    def to_string(self):
        return "_".join([self.resource_name, self.command, *self.arguments])

class QESPPos(QResource):
        
    message_received = pyqtSignal(str)

    def __init__(self, resource):

        # reinitialize QResource class
        super().__init__(resource)

        self.timer = QTimer()
        self.timer.setInterval(self.config["timer_interval"])
        self.timer.timeout.connect(self.on_timer)

        # Update interfaces
        for key in self.interfaces:
            self.interfaces[key].master = self
        self.master_int.slaves[self.name] = self

    def open(self):

        pyvisa_address = self.config["pyvisa"]["address"]
        self.pyvisa_handler = pyvisa.ResourceManager().open_resource(pyvisa_address)
        
        self.pyvisa_handler.baud_rate = self.config["pyvisa"]["baud_rate"]
        self.pyvisa_handler.read_termination = self.config["pyvisa"]["read_termination"]
        self.pyvisa_handler.write_termination = self.config["pyvisa"]["write_termination"]
        self.pyvisa_handler.timeout = self.config["pyvisa"]["timeout"]

        self.timer.start()

    def read_message(self):
        # print("reading: ", end='')
        message = self.pyvisa_handler.read()
        # print(message)
        self.message_received.emit(message)
        # time.sleep(self.config["comm_delay"])
        
        return message

    def send_message(self, message):
        self.pyvisa_handler.write(message)
        # print("echoing:", self.pyvisa_handler.read()) # skip echo
        # time.sleep(self.config["comm_delay"]*1e-3)

    def query_message(self, message):
        self.send_message(message)
        return self.read_message()

    def on_timer(self):

        # print("esp.timeout >>> ")
        try:
            msg = QESPPosMessage(self.read_message())
            # print(">>", msg.resource_name, msg.command, msg.arguments, end='\t')
            # print(">>", self.slaves[msg.resource_name])
            self.slaves[msg.resource_name].parse(msg.command, msg.arguments)
        except pyvisa.errors.VisaIOError:
            pass
