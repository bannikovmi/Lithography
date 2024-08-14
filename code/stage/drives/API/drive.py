from PyQt5.QtCore import pyqtSignal, QTimer

from backend.resources.resource import QResource

class QDrive(QResource):
    
    movement_status = pyqtSignal(bool)
    max_checked = pyqtSignal(int)
    min_checked = pyqtSignal(int)

    props = {
        "speed": "SPD",
        "mstep": "MST",
        "power": "POW",
        "max": "MAX",
        "min": "MIN",
        "irun": "IRN"
    }

    def __init__(self, resource):

        super().__init__(resource)

        # master resource
        self.esp = self.master_int.master
        self.is_moving = False
        self.nsteps = 0

    def start_movement(self, nsteps):

        self.nsteps = nsteps
        self.movement_status.emit(True)

        # Construct timer for limit checking and launch it
        self.timer = QTimer()
        self.timer.setInterval(self.config["limits_check_interval"])
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()

        # Send message to start movement
        self.esp.send_message(f"{self.name}_MOV_{nsteps}")
        self.is_moving = True

    def on_timer(self):

        self.request("max")
        self.request("min")

    def abort_movement(self):

        self.esp.send_message(f"{self.name}_MOV_ABT")
        self.on_movement_finish()

    def on_movement_finish(self):

        self.timer.stop()
        
        self.is_moving = False
        self.movement_status.emit(False)
        self.request("max")
        self.request("min")

    def request(self, key):
        self.esp.send_message(f"{self.name}_{self.props[key]}")
        
    def set(self, key, val):
        self.esp.send_message(f"{self.name}_{self.props[key]}_{val}")

    def parse(self, command, arguments):

        try:
            if command == "MAX":
                state = int(arguments[0])
                self.max_checked.emit(state)
                if self.is_moving and state and self.nsteps > 0:
                    self.abort_movement()
            elif command == "MIN":
                state = int(arguments[0])
                self.min_checked.emit(state)
                if self.is_moving and state and self.nsteps < 0:
                    self.abort_movement()
            elif command == "MOV":
                if arguments[0] == "FIN":
                    self.on_movement_finish()
        except IndexError:
            pass
