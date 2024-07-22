# third-party imports
import pyvisa

# pyqt-related imports
from PyQt5.QtCore import QObject, QTimer

class Message:

    def __init__(self, message=""):

        split_message = message.split("_")
        self.resource_name = split_message[0]
        self.command_name = split_message[1]
        self.arguments = split_message[2:]

class ESP(QObject):

    def __init__(self, config, simulation=False):

        super().__init__()

        self.config = config
        self.is_finished = False
        self.simulation = simulation

        # Open pyvisa session and configure the device
        self.rm = pyvisa.ResourceManager()
        self.resource = self.rm.open_resource(
            self.config["Communicator"]["pyvisa"]["address"])

        baud_rate = self.config["Communicator"]["pyvisa"]["baud_rate"]
        read_termination = self.config["Communicator"]["pyvisa"]["read_termination"]
        write_termination = self.config["Communicator"]["pyvisa"]["write_termination"]
        timeout = self.config["Communicator"]["pyvisa"]["timeout"]

        self.resource.baud_rate = baud_rate
        self.resource.read_termination = read_termination
        self.resource.write_termination = write_termination
        self.resource.timeout = timeout

        self.timer = QTimer()
        self.timer.setInterval(self.config["Communicator"]["polling_interval"])
        self.timer.timeout.connect(self.on_timer)

    def write(self, message):
        if not self.simulation:
            self.resource.write(message)

    def read(self):
        if not self.simulation:
            return self.resource.read()
        else:
            return ""

    def query(self, message):
        if not self.simulation:
            return self.resource.query(message)

    def on_timer(self):

        if not self.simulation:
            try: 
                message = Message(self.read())
                resource_name = message.resource_name
                command_name = message.command_name
                arguments = message.arguments
                if resource_name == "TMG":
                    return
                print(resource_name, command_name, arguments)
                self.resource_widgets[resource_name].update_UI(
                    resource_name, command_name, arguments)

            except pyvisa.errors.VisaIOError:
                pass
