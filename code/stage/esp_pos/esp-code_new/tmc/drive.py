from machine import Timer, Pin, UART

import math

# local imports
from resource.resource import Resource
from tmc.movement import Movement
import tmc.reg as reg

class Drive(Resource):

    drive_commands = {
        "POW": "power",
        "SPD": "speed",
        "MOV": "move",
        "POS": "position",
        "MAX": "at_max",
        "MIN": "at_min",
        "MXL": "max_lim",
        "MNL": "min_lim",
        "STS": "status",
        "MST": "microstep",
        "IRN": "irun",
    }

    # merge with parent commands
    available_commands = Resource.available_commands | drive_commands

    def __init__(self, esp, name):
    
        super().__init__()
    
        # Save esp resource instance and name
        self.esp = esp
        self.name = name

        # Load config
        self.config = self.esp.config[name]

        # Initialize ESP pins
        self.step_pin = Pin(self.config["step_id"], mode=Pin.OUT)
        self.min_pin = Pin(self.config["min_id"], Pin.IN, Pin.PULL_UP)
        self.max_pin = Pin(self.config["max_id"], Pin.IN, Pin.PULL_UP)

        # Deterimine limit trigger
        if self.config["limit_on"] == 1:
            self.limit_trigger = Pin.IRQ_RISING
        else:
            self.limit_trigger = Pin.IRQ_FALLING

        # Disable drive power on startup
        self.power(0)

        # Set default parametres
        self.speed(self.config["speed"])
        self.irun(self.config["irun"])
        self.microstep(self.config["microstep"])
        self.max_lim(self.config["max_en"])
        self.min_lim(self.config["min_en"])

    ##########################################################################################
    #### Read-only methods
    ##########################################################################################
    def at_max(self):

        if self.max_en:
            val = (self.max_pin.value() == self.config["limit_on"])
        else:
            val = None
        
        print(f"{self.name}_MAX_{int(val)}")

    def at_min(self):
        
        if self.min_en:
            val = (self.min_pin.value() == self.config["limit_on"])
        else:
            val = None
        
        print(f"{self.name}_MIN_{int(val)}")

    def position(self, val=None):
        
        if val is None:
            print(f"{self.name}_POS_{self.config["pos"]}")
        else:
            self.config["pos"] = int(val)
            
    def status(self):
        
        if self.max_en:
            at_max = (self.max_pin.value() == self.config["limit_on"])
        else:
            at_max = None
        if self.min_en:
            at_min = (self.min_pin.value() == self.config["limit_on"])
        else:
            at_min = None
        
        print(f"{self.name}_STS_{self.config["pos"]}_{int(at_min)}_{int(at_max)}")

    ##########################################################################################
    #### Write-only methods
    ##########################################################################################
    def mstep_res_select(self, en):
        
        gconf = self.esp.tmc_uart.read_int(self.config["mtr_id"], reg.GCONF)
        
        if(en == True):
            gconf = self.esp.tmc_uart.set_bit(gconf, reg.mstep_reg_select)
        else:
            gconf = self.esp.tmc_uart.clear_bit(gconf, reg.mstep_reg_select)

        self.esp.tmc_uart.write_reg_check(self.config["mtr_id"], reg.GCONF, gconf)

    ##########################################################################################
    #### Read and write methods
    ##########################################################################################
    # Methods not referenced from host via IO-commands
    def direction(self, val=None):
        
        pos_dir = self.config["pos_dir"]
        
        if val is None:
            val = self.esp.pcf.pin(self.config["dir_id"])
            return -1 + 2 * (val == pos_dir) # +1 if val == pos_dir else -1
        else:
            set_val = pos_dir if int(val) == 1 else not pos_dir
            self.esp.pcf.pin(self.config["dir_id"], set_val)
                
    # Methods referenced from host via IO-commands
    def power(self, state=None):
        
        if state is None:
            _power = int(not self.esp.pcf.pin(self.config["en_id"]))
            print(f"{self.name}_POW_{_power}")
        else:
            _power = int(state)
            self.esp.pcf.pin(self.config["en_id"], not _power) # Setting pin to low enables drive power

    def max_lim(self, val=None):
        
        if val is None:
            print(f"{self.name}_MXL_{self.max_en}")
        else:
            self.max_pin(val)
            self.max_en = int(val)
            
    def min_lim(self, val=None):
        
        if val is None:
            print(f"{self.name}_MNL_{self.min_en}")
        else:
            self.min_pin(val)
            self.min_en = int(val)

    def speed(self, value=None):
    
        if value is None:
            print(f"{self.name}_SPD_{self._speed}")
        else:
            self._speed = int(value)

    def microstep(self, msres=None):
        
        if msres is None:

            chopconf = self.esp.tmc_uart.read_int(self.config["mtr_id"], reg.CHOPCONF)
            msresdezimal = chopconf & (reg.msres0 | reg.msres1 | reg.msres2 | reg.msres3)
            msresdezimal = msresdezimal >> 24
            msresdezimal = 8 - msresdezimal
            msres = int(math.pow(2, msresdezimal))
            print(f"{self.name}_MST_{msres}")

        else:

            self._msres = int(msres)
            chopconf = self.esp.tmc_uart.read_int(self.config["mtr_id"], reg.CHOPCONF)

            # Set all bits to zero
            chopconf = chopconf & (~reg.msres0 | ~reg.msres1 | ~reg.msres2 | ~reg.msres3)
            msresdezimal = int(math.log(int(msres), 2))
            msresdezimal = 8 - msresdezimal
            chopconf = int(chopconf) & int(4043309055)
            chopconf = chopconf | msresdezimal << 24
            
            self.esp.tmc_uart.write_reg_check(self.config["mtr_id"], reg.CHOPCONF, chopconf)
            self.mstep_res_select(True)

    def irun(self, val=None):
        
        if val is None:
            print(f"{self.name}_IRN_{self._irun}")
            return self._irun
        else:
            self._irun = int(val)
            ihold_irun = 0 | self._irun << 8
            self.esp.tmc_uart.write_reg_check(self.config["mtr_id"], reg.IHOLD_IRUN, ihold_irun)
        
    ##########################################################################################
    #### Movement-related methods
    ##########################################################################################        
    def move(self, nsteps=None):

        # Check that power is on
        power_off = self.esp.pcf.pin(self.config["en_id"])
        if power_off:
            print(f"{self.name}_POW_OFF")
            return

        name = f"{self.name}_MOV"

        if nsteps == "ABT":
            self.esp.task_manager.abort_task(name)
        elif nsteps == None:
            try:
                counter = self.esp.task_manager.tasks[name].counter
                nsteps = self.esp.task_manager.tasks[name].nsteps * self.direction()
                print(f"{name}_{counter}:{nsteps}")
            except KeyError:
                print(f"{name}_NONE")
        else:
            try:
                movement = Movement(name=name, drive=self, nsteps=int(nsteps))
                self.esp.task_manager.start_task(movement)
            except Exception as e:
                print(e)
