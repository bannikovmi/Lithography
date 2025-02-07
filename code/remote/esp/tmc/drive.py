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
        "MAX": "at_max",
        "MIN": "at_min",
        "MST": "mstep",
        "IRN": "irun",
        "STS": "status",
        "MOV": "move",
        "POS": "pos",
    }

    # merge with parent commands
    available_commands = Resource.available_commands | drive_commands

    def __init__(self, esp, name):
    
        super().__init__(name)
        self.esp = esp

        # Initialize ESP pins
        self.dir_pin = Pin(self.config["ids"]["dir"], mode=Pin.OUT)
        self.step_pin = Pin(self.config["ids"]["step"], mode=Pin.OUT)

        # Save motor id
        self.mtr_id = self.config["ids"]["mtr"]

        # Save PCF pin id's
        self.en_id = self.config["ids"]["en"]
        self.min_id = self.config["ids"]["min"]
        self.max_id = self.config["ids"]["max"]

        # Deterimine limit trigger
        if self.config["limit_on"] == 1:
            self.limit_trigger = Pin.IRQ_RISING
        else:
            self.limit_trigger = Pin.IRQ_FALLING

        # Disable drive power on startup
        self.power(0)

        # Pull PCF min and max pins high to work as limit switchers
        self.esp.pcf.pin(self.min_id, 1)
        self.esp.pcf.pin(self.max_id, 1)

        # Set default parametres
        self.speed(self.config["speed"]["default"])
        self.irun(self.config["irun"]["default"])
        self.mstep(self.config["mstep"]["default"])
        
        # Load position from config
        self._pos = self.config["pos"]

    ##########################################################################################
    #### Properties
    ##########################################################################################
    @property
    def direction(self):
        val = self.dir_pin()
        pos_dir = self.config["pos_dir"]
        if val == pos_dir:
            return 1
        else:
            return -1
    
    @direction.setter
    def direction(self, value):
        if int(value) == 1:
            self.dir_pin(self.config["pos_dir"])
        else:
            self.dir_pin(not self.config["pos_dir"])

    ##########################################################################################
    #### Host IO commands
    ##########################################################################################
    def power(self, state=None):
        
        if state is None:
            self._power = int(not self.esp.pcf.pin(self.en_id))
            print(f"{self.name}_POW_{self._power}")
        else:
            self._power = int(state)
            self.esp.pcf.pin(self.en_id, not self._power) # Setting pin to low enables drive power

    def speed(self, value=None):
    
        if value is None:
            print(f"{self.name}_SPD_{self._speed}")
        else:
            self._speed = int(value)

    def pos(self):
        print(f"{self.name}_POS_{self._pos}")

    def move(self, nsteps=None):

        name = f"{self.name}_MOV"

        if nsteps == "ABT": # abort movement
            counter = self.esp.task_manager.tasks[name].counter
            self.esp.task_manager.abort_task(name)
            print(f"{self.name}_MOV_FIN_{counter}")
        elif nsteps == None: # check movement status
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

        if self.esp.pcf.pin(self.max_id) == self.config["limit_on"]:
            print(f"{self.name}_MAX_1")
            return True
        else:
            print(f"{self.name}_MAX_0")
            return False

    def at_min(self):

        if self.esp.pcf.pin(self.min_id) == self.config["limit_on"]:
            print(f"{self.name}_MIN_1")
            return True
        else:
            print(f"{self.name}_MIN_0")
            return False

    def mstep(self, msres=None):
        
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

        self._mstep = int(msres)

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
            
    def status(self):
        
        at_min = int(self.esp.pcf.pin(self.min_id) == self.config["limit_on"])
        at_max = int(self.esp.pcf.pin(self.max_id) == self.config["limit_on"])
        print(f"{self.name}_STS_{at_min}_{at_max}_{self._pos}")
        
        # Update drive position in config
        self.config["pos"] = self._pos
        self.dump_config()

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
            int_id = self.drive.config["ids"]["max"]
        else:    

            # Ensure we are not at min
            if self.drive.at_min():
                raise Exception(f"{self.name}_MIN")
            self.drive.direction = -1
            int_name = f"{self.name}_MIN"
            int_id = self.drive.config["ids"]["min"]            
        
        self.nsteps = abs(nsteps)
        self.counter = 0
        self.single_step = self.drive.direction * 256//self.drive._mstep

        init_val = not self.drive.config["limit_on"]
        self.interrupt = MovementInterrupt(int_name, int_id, init_val)

    def callback(self, t):

        # print(f"{self.name} callback {self.counter}")

        if self.counter < self.nsteps:
            self.counter += 1
            self.drive._pos += self.single_step # Update drive position
            self.drive.step_pin(not self.drive.step_pin()) # Toggle step pin
        else:
            self.finished = True
            print(f"{self.drive.name}_MOV_FIN_{self.counter}")

    def finish(self):

        # Just in case pull min and max pins high once again
        self.drive.esp.pcf.pin(self.drive.max_id, 1)
        self.drive.esp.pcf.pin(self.drive.min_id, 1)

class MovementInterrupt:

    def __init__(self, name, int_id, init_val):

        self.name = name
        self.int_id = int_id
        self.init_val = init_val

