# third-party imports
from pyvisa.errors import VisaIOError

# pyqt-related imports
from PyQt5.QtCore import QObject, QTimer

class Message:

    def __init__(self, message=""):

        split_message = message.split("_")
        self.resource_name = split_message[0]
        self.command_name = split_message[1]
        self.arguments = split_message[2:]

class CommunicationMode:

    simulation = False
    communication = True

class ESP(QObject):

    def __init__(self, config, mode=CommunicationMode.communication):

        super().__init__()

        self.config = config
        self.ESP = ESP
        self.is_finished = False
        self.mode = mode

        self.timer = QTimer()
        self.timer.setInterval(self.config["Listener"]["polling_interval"])
        self.timer.timeout.connect(self.on_timer)

    def write(self, message):
        if self.mode:
            self.serial.write(message)

    def read(self):
        if self.mode:
            return self.serial.read()
        else:
            return ""

    def query(self, message):
        self.write(message)
        return self.read()

    def muter_query(self, message):
        # Remake after threads are introduced
        return self.query(message)

    def on_timer(self):

        if self.mode:
            message = Message(self.read())
            resource_name = message.resource_name
            command_name = message.command_name
            arguments = message.arguments
            if resource_name == "TMG":
                return
            print(resource_name, command_name, arguments)
            self.resource_widgets[resource_name].update_UI(
                resource_name, command_name, arguments)
        else:
            pass

        # try:
        #     message = Message(self.read())
        #     resource_name = message.resource_name
        #     command_name = message.command_name
        #     arguments = message.arguments
        #     if resource_name == "TMG":
        #         return
        #     print(resource_name, command_name, arguments)
        #     self.widgets[resource_name].update_UI(resource_name, command_name, arguments)

        # except VisaIOError:
        #     pass
