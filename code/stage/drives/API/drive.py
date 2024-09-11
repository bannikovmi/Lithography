import numpy as np

from PyQt5.QtCore import pyqtSignal, QTimer

from backend.resources.resource import QResource
from stage.drives.API.position import DrivePosition
from stage.drives.API.movement import MovementRunner

class QDrive(QResource):
    
    movement_started = pyqtSignal()
    movement_finished = pyqtSignal()
    max_checked = pyqtSignal(int)
    min_checked = pyqtSignal(int)
    pos_updated = pyqtSignal(DrivePosition)

    props = {
        "speed": "SPD",
        "mstep": "MST",
        "power": "POW",
        "max": "MAX",
        "min": "MIN",
        "irun": "IRN",
        "status": "STS"
    }

    def __init__(self, resource):

        super().__init__(resource)

        # master resource
        self.esp = self.master_int.master
        
        # hidden attributes
        self._mstep = self.config["mstep"]
        self._speed = self.config["speed"]

        # auxiliary attributes
        self.is_moving = False
        self.nsteps = 0

    ##########################################################################################
    ### Property-related functions
    ##########################################################################################
    def get(self, key):
        message = self.esp.query(f"{self.name}_{self.props[key]}")
        return message.split("_")[2]

    def set(self, key, val):
        setattr(self, f"_{key}", val) # update hidden attribute
        self.esp.write(f"{self.name}_{self.props[key]}_{val}")

    def update_status(self):
        message = self.esp.query(f"{self.name}_STS")
        print(f"in {self.name} update_status: received {message}")

        try:
            ret = message.split("_")[2:]
        except Exception as e:
            print(e)
            self.update_status()

        at_min = int(ret[0])
        at_max = int(ret[1])
        
        self.pos = DrivePosition(int(ret[2]), 256)
        self.dump_config()

        self.is_moving = int(ret[3])
        self.min_checked.emit(at_min)
        self.max_checked.emit(at_max)
        self.pos_updated.emit(self.pos)
    ##########################################################################################
    ### Movement-related commands 
    ##########################################################################################
    def move_nsteps(self, nsteps):

        self.movement_runner = MovementRunner(self, nsteps)

        self.movement_runner.signals.started.connect(self.movement_started)
        self.movement_runner.signals.finished.connect(self.movement_finished)

        # is_moving flag should be set in the same thread that launches move_nsteps
        self.is_moving = True

        self.thread_pool.start(self.movement_runner)

        # # Construct timer for status checking and launch it
        # self.request_timer = QTimer()
        # self.request_timer.setInterval(self.config["status_check_interval"])
        # self.request_timer.timeout.connect(lambda: self.request("status"))
        # self.request_timer.start()

    def abort_movement(self):

        if self.is_moving:
            self.esp.write(f"{self.name}_ABT")

    def launch_movement(self, nsteps):

        self.esp.write(f"{self.name}_MOV_{nsteps}")

    def check_finish(self):

        return self.esp.read() == f"{self.name}_FIN"


    # def parse(self, command, arguments):

    #     try:
    #         if command == "STS": # update movement status

    #             # parse command
    #             at_min = int(arguments[0])
    #             at_max = int(arguments[1])
                
    #             # Emit signals
    #             self.max_checked.emit(at_max)
    #             self.min_checked.emit(at_min)

    #             # Check if movement should be aborted
    #             if self.is_moving and at_min and self.nsteps < 0:
    #                 self.abort_movement()
    #             elif self.is_moving and at_max and self.nsteps > 0:
    #                 self.abort_movement()

    #             # Update position
    #             pos_256 = int(arguments[2])
    #             self.pos = DrivePosition(Fraction(pos_256, 256))

    #             self.pos_updated.emit(self.pos)
    #             self.config["pos"] = self.pos.to_json()
    #             self.dump_config()

    #         elif command == "FIN":
    #             self.on_movement_finish()
                
    #     except Exception as e:
    #         print(f"in {self.name}, parse: received command " +
    #             f"{command}, arguments: {arguments}, exception: {e}")
