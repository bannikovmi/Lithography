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

class Listener(QObject):

    def __init__(self, config, ESP, widgets):

        super().__init__()

        self.config = config
        self.ESP = ESP
        self.widgets = widgets
        self.is_finished = False

        self.timer = QTimer()
        self.timer.setInterval(self.config["Listener"]["polling_interval"])
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()

    def on_timer(self):

        try:
            message = Message(self.ESP.read())
            resource_name = message.resource_name
            command_name = message.command_name
            arguments = message.arguments
            if resource_name == "TMG":
                return
            print(resource_name, command_name, arguments)
            self.widgets[resource_name].update_UI(resource_name, command_name, arguments)

        except VisaIOError:
            pass