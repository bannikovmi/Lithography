# standart library imports
import time

# third-party imports
import pyvisa

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, QTimer

# local imports
from backend.resources.resource import QResource
from backend.resources.manager import ExecutionMode
from stage.esp.comm import ESPCommRunner

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

        # self.timer = QTimer()
        # self.timer.setInterval(self.config["timer_interval"])
        # self.timer.timeout.connect(self.on_timer)

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

        self.comm_runner = ESPCommRunner(self.pyvisa_handler)

        # connect signals
        self.comm_runner.signals.message_received.connect(self.message_received)
        self.thread_pool.start(self.comm_runner)

        # self.timer.start()

    def write(self, message):
        self.comm_runner.write(message)

    def query(self, message):
        return self.comm_runner.query(message)

    # def read_message(self):
    #     message = self.pyvisa_handler.read()
    #     self.message_received.emit(message)
    #     return message

    # def send_message(self, message):
    #     self.pyvisa_handler.write(message)
    #     self.pyvisa_handler.read() # skip echo
    #     # print("echoing:", self.pyvisa_handler.read()) # skip echo

    # def query_message(self, message):
    #     self.mutex.lock()
    #     self.send_message(message)
    #     ret = self.read_message()
    #     self.mutex.unlock()
    #     return ret

    # def on_timer(self):

    #     # print("esp.timeout >>> ")
    #     try:
    #         msg = QESPPosMessage(self.read_message())
    #         print(">>", msg.resource_name, msg.command, msg.arguments)
    #         # print(">>", self.slaves[msg.resource_name])
    #         self.slaves[msg.resource_name].parse(msg.command, msg.arguments)
    #     except pyvisa.errors.VisaIOError:
    #         pass
