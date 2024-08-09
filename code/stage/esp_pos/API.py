# third-party imports
import pyvisa

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, QTimer

# local imports
from backend.resources.resource import QResource

class QESPPosMessage:

    def __init__(self, message=""):

        split_message = message.split("_")
        self.resource_name = split_message[0]
        self.command_name = split_message[1]
        self.arguments = split_message[2:]

    def to_string(self):
        return "_".join([self.resource_name, self.command_name, *self.arguments])

class QESPPos(QResource):
        
    message_received = pyqtSignal(QESPPosMessage)

    def __init__(self, resource):

        # reinitialize QResource class
        super().__init__(resource)

        self.timer = QTimer()
        self.timer.setInterval(self.config["timer_interval"])
        self.timer.timeout.connect(self.on_timer)

    def open(self):

        pyvisa_address = self.config["pyvisa"]["address"]
        self.pyvisa_handler = pyvisa.ResourceManager().open_resource(pyvisa_address)
        
        self.baud_rate = self.config["pyvisa"]["baud_rate"]
        self.read_termination = self.config["pyvisa"]["read_termination"]
        self.write_termination = self.config["pyvisa"]["write_termination"]
        self.timeout = self.config["pyvisa"]["timeout"]  

    def read_message(self):
        message = QMessage(self.pyvisa_handler.read())
        self.message_received.emit(message)
        return message

    def send_message(self, message):
        self.pyvisa_handler.write(message)

    def on_timer(self):

        try:
            self.read_message()
        except pyvisa.errors.VisaIOError:
            pass
