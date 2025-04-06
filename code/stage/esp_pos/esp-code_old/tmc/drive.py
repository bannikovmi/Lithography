from machine import Timer, Pin, UART

import math

# local imports
from resource.resource import Resource
from ESP.tasks import LastingTask
import tmc.reg as reg

class Drive(Resource):

    drive_commands = {
        "POW": "power",
        "SPD": "speed",
        "MOV": "move",
        "MAX": "at_max",
        "MIN": "at_min",
        "MST": "microstep",
        "IRN": "irun",
    }

    # merge with parent commands
    available_commands = Resource.available_commands | drive_commands

    def __init__(self, esp, name):
    
        # Save esp resource instance and name
        self.esp = esp
        self.name = name

        # Initialize ESP pins
        self.dir_pin = Pin(self.esp.config[name]["dir_id"], mode=Pin.OUT)
        self.step_pin = Pin(self.esp.config[name]["step_id"], mode=Pin.OUT)

        # Save motor id
        self.mtr_id = self.esp.config[name]["mtr_id"]

        # Save PCF pin id's
        self.en_id = self.esp.config[name]["en_id"]
        self.min_id = self.esp.config[name]["min_id"]
        self.max_id = self.esp.config[name]["max_id"]

        # Deterimine limit trigger
        if self.esp.config[name]["limit_on"] == 1:
            self.limit_trigger = Pin.IRQ_RISING
        else:
            self.limit_trigger = Pin.IRQ_FALLING

        # Disable drive power on startup
        self.power(0)

        # Pull PCF min and max pins high to work as limit switchers
        self.esp.pcf.pin(self.min_id, 1)
        self.esp.pcf.pin(self.max_id, 1)

        # Set default parametres
        self.speed(self.esp.config[name]["speed"])
        self.irun(self.esp.config[name]["irun"])
        self.microstep(self.esp.config[name]["microstep"])

    ##########################################################################################
    #### Properties
    ##########################################################################################
    @property
    def direction(self):
        val = self.dir_pin()
        pos_dir = self.esp.config[self.name]["pos_dir"]
        if val == pos_dir:
            return 1
        else:
            return -1
    
    @direction.setter
    def direction(self, value):
        if int(value) == 1:
            self.dir_pin(self.esp.config[self.name]["pos_dir"])
        else:
            self.dir_pin(not self.esp.config[self.name]["pos_dir"])

    ##########################################################################################
    #### Host IO commands
    ##########################################################################################
    def power(self, state=None):
        
        if state is None:
            _power = int(not self.esp.pcf.pin(self.en_id))
            print(f"{self.name}_POW_{_power}")
        else:
            _power = int(state)
            self.esp.pcf.pin(self.en_id, not _power) # Setting pin to low enables drive power

    def speed(self, value=None):
    
        if value is None:
            print(f"{self.name}_SPD_{self._speed}")
        else:
            self._speed = int(value)

    def move(self, nsteps=None):

        name = f"{self.name}_MOV"

        if nsteps == "ABT":
            self.esp.task_manager.abort_task(name)
        elif nsteps == None:
            try:
                counter = self.esp.task_manager.tasks[name].counter
                nsteps = self.esp.task_manager.tasks[name].nsteps * self.direction
                print(f"{name}_{counter}:{nsteps}")
            except KeyError:
                print(f"{name}_NONE")
        else:
            try:
                movement = Movement(name=name, drive=self, nsteps=int(nsteps))
                self.esp.task_manager.start_task(movement)
            except Exception as e:
                print(e)

    def at_max(self):

        if self.esp.pcf.pin(self.max_id) == self.esp.config[self.name]["limit_on"]:
            print(f"{self.name}_MAX_1")
            return True
        else:
            print(f"{self.name}_MAX_0")
            return False

    def at_min(self):

        if self.esp.pcf.pin(self.min_id) == self.esp.config[self.name]["limit_on"]:
            print(f"{self.name}_MIN_1")
            return True
        else:
            print(f"{self.name}_MIN_0")
            return False

    def microstep(self, msres=None):
        
        if msres is None:

            chopconf = self.esp.tmc_uart.read_int(self.mtr_id, reg.CHOPCONF)
            msresdezimal = chopconf & (reg.msres0 | reg.msres1 | reg.msres2 | reg.msres3)
            msresdezimal = msresdezimal >> 24
            msresdezimal = 8 - msresdezimal
            msres = int(math.pow(2, msresdezimal))
            print(f"{self.name}_MST_{msres}")

        else:

            chopconf = self.esp.tmc_uart.read_int(self.mtr_id, reg.CHOPCONF)

            # Set all bits to zero
            chopconf = chopconf & (~reg.msres0 | ~reg.msres1 | ~reg.msres2 | ~reg.msres3)
            msresdezimal = int(math.log(int(msres), 2))
            msresdezimal = 8 - msresdezimal
            chopconf = int(chopconf) & int(4043309055)
            chopconf = chopconf | msresdezimal << 24
            
            self.esp.tmc_uart.write_reg_check(self.mtr_id, reg.CHOPCONF, chopconf)
            self.mstep_res_select(True)

    def mstep_res_select(self, en):
        
        gconf = self.esp.tmc_uart.read_int(self.mtr_id, reg.GCONF)
        
        if(en == True):
            gconf = self.esp.tmc_uart.set_bit(gconf, reg.mstep_reg_select)
        else:
            gconf = self.esp.tmc_uart.clear_bit(gconf, reg.mstep_reg_select)

        self.esp.tmc_uart.write_reg_check(self.mtr_id, reg.GCONF, gconf)

    def irun(self, val=None):
        
        if val is None:
            print(f"{self.name}_IRN_{self._irun}")
            return self._irun
        else:
            self._irun = int(val)
            ihold_irun = 0 | self._irun << 8
            self.esp.tmc_uart.write_reg_check(self.mtr_id, reg.IHOLD_IRUN, ihold_irun)

class Movement(LastingTask):

    def __init__(self, name, drive, nsteps=1):

        self.drive = drive

        super().__init__(name=name, mode=Timer.PERIODIC, freq=drive._speed)

        # Just in case pull min and max pins high once again
        self.drive.esp.pcf.pin(self.drive.max_id, 1)
        self.drive.esp.pcf.pin(self.drive.min_id, 1)

        if nsteps > 0:             

            # Ensure we are not at max
            if self.drive.at_max():
                raise Exception(f"{self.name}_MAX")

            self.drive.direction = 1
            
            int_name = f"{self.name}_MAX"
            int_id = self.drive.esp.config[self.drive.name]["max_id"]
        else:    

            # Ensure we are not at min
            if self.drive.at_min():
                raise Exception(f"{self.name}_MIN")
            self.drive.direction = -1
            int_name = f"{self.name}_MIN"
            int_id = self.drive.esp.config[self.drive.name]["min_id"]            
        
        self.nsteps = abs(nsteps)
        self.counter = 0

        init_val = not self.drive.esp.config[self.drive.name]["limit_on"]
        self.interrupt = MovementInterrupt(int_name, int_id, init_val)

    def callback(self, t):

        # print(f"{self.name} callback {self.counter}")

        if self.counter < self.nsteps:
            self.counter += 1
            self.drive.step_pin(not self.drive.step_pin()) # Toggle step pin
        else:
            self.finished = True
            print(f"{self.drive.name}_MOV_FIN")

    def finish(self):

        # Just in case pull min and max pins high once again
        self.drive.esp.pcf.pin(self.drive.max_id, 1)
        self.drive.esp.pcf.pin(self.drive.min_id, 1)

class MovementInterrupt:

    def __init__(self, name, int_id, init_val):

        self.name = name
        self.int_id = int_id
        self.init_val = init_val

