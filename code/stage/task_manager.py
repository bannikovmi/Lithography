# third-party imports
from pyvisa.errors import VisaIOError

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, QObject, QTimer

# local imports
from .esp import ESP

class QMessage(QObject):

    def __init__(self, message=""):

        split_message = message.split("_")
        self.resource_name = split_message[0]
        self.command_name = split_message[1]
        self.arguments = split_message[2:]

class QTaskManager(QObject):

    message_received = pyqtSignal(QMessage)

    def __init__(self, config, simulation=False):

        self.config = config
        self.simulation = simulation
        # self.esp = ESP(self.config)
        super().__init__()

        self.timer = QTimer()
        self.timer.setInterval(self.config["Task_manager"]["polling_interval"])
        self.timer.timeout.connect(self.on_timer)

    def on_timer(self):

        if not self.simulation:

            try: 
                message = QMessage(self.esp.read())
                self.message_received.emit(message)

            except VisaIOError:
                pass
