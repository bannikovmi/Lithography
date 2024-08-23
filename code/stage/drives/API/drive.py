from fractions import Fraction

import numpy as np

from PyQt5.QtCore import pyqtSignal, QTimer

from backend.resources.resource import QResource

class DrivePosition(Fraction):

    def to_improper(self):

        num = self.numerator
        den = self.denominator

        quot = num // den
        rem = num % den

        if rem == 0:
            return f"{quot}", ""
        else:
            if quot >= 0:
                return f"{quot}", f"{rem}/{den}"
            else:
                if quot == -1:
                    return f"{quot+1}", f"{rem-den}/{den}"
                else:
                    return f"{quot+1}", f"{den-rem}/{den}"

    def to_json(self):

        return [int(self.numerator), int(self.denominator)]

class QDrive(QResource):
    
    movement_started = pyqtSignal()
    movement_finished = pyqtSignal()
    max_checked = pyqtSignal(int)
    min_checked = pyqtSignal(int)
    pos_updated = pyqtSignal(Fraction)

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
        self.pos = DrivePosition(*self.config["pos"])
        
        self._mstep = self.config["mstep"]
        self._speed = self.config["speed"]

    def start_movement(self, nsteps):

        self.nsteps = nsteps
        self.movement_started.emit()

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
        self.movement_finished.emit()
        self.request("max")
        self.request("min")

    def request(self, key):
        self.esp.send_message(f"{self.name}_{self.props[key]}")
        
    def set(self, key, val):
        setattr(self, f"_{key}", val) # update hidden attribute
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

                    # After movement finish ESP will send messages like MOV_FIN_XXX,
                    # Where XXX is the absolute value of msteps made
                    # We need to update self.pos attribute and config file
                    pos_shift = Fraction(self.config["pos_direction"]*
                        np.sign(self.nsteps)*int(arguments[1]), self._mstep)
                    self.pos = DrivePosition(self.pos + pos_shift)
                    self.pos_updated.emit(self.pos)
                    self.config["pos"] = self.pos.to_json()
                    self.dump_config()
                
        except IndexError:
            pass
