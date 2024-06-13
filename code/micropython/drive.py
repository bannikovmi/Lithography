from machine import Timer, Pin

# local imports
from resource import Resource
from tasks import LastingTask

class Drive(Resource):

    POS = 1
    NEG = 0

    drive_commands = {
        "POW": "power",
        "SPD": "speed",
        "MOV": "move",
        "MAX": "at_max",
        "MIN": "at_min",
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
        # self.direction(self.esp.config[name]["direction"])

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
            self._power = int(not self.esp.pcf.pin(self.en_id))
            print(f"{self.name}_POW_{self._power}")
        else:
            self._power = int(state)
            self.esp.pcf.pin(self.en_id, not self._power) # Setting pin to low enables drive power

    def speed(self, value=None):
    
        if value is None:
            print(f"{self.name}_POW_{self._speed}")
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

        # if nsteps is None: # Return state

        #     if self.timer is None: # No movement
        #         print(f"{self.name}_MOV_NONE")
        #     else: # Movement is in place, return counter
        #         print(f"{self.name}_MOV_{self.nsteps}_{self.counter}")
        
        # else: # Perform movement

        #     if self.timer is not None: # A move operation is already in place
        #         print(f"{self.name}_MOV_BUSY")
        #     else:
        #         # Save nsteps to local variable for use in timeout handler
        #         self.nsteps = int(nsteps)

        #         if self.nsteps > 0:
        #             # Check that the positioner is not currently at max
        #             if self.esp.pcf.pin(self.max_id) == self.esp.config[name]["limit_on"]:
        #                 print(f"{self.name}_MOV_MAX")
        #                 return
        #             else:
        #                 self.direction(1)
                
        #         else:
        #             # Check that the positioner is not currently at min
        #             if self.esp.pcf.pin(self.min_id) == self.esp.config[name]["limit_on"]:
        #                 print(f"{self.name}_MOV_MIN")
        #                 return
        #             else:
        #                 self.direction(-1)

        #         self.counter = 0

        #         # Initialize timer
        #         self.timer_id = self.esp.allocate_timer_id()
        #         self.timer = Timer(self.timer_id)
        #         self.timer.init(mode=Timer.PERIODIC, freq=int(self.speed()),
        #             callback=lambda t: self.on_timer_event())
        
    # def on_timer(self):

    #     if self.counter < self.n_steps:
    #         self.step_pin(not self.step_pin()) # Toggle step pin
    #         self.counter += 1
    #     else:
    #         if self.timer is not None:
    #             self.timer.deinit()
    #             self.esp.deallocate_timer(self.timer_id)
    #             self.timer = None
    #             print(f"{self.name}_MOV_END")

    # def on_min(self):

    #     if self.esp.pcf.pin(self.min_id) == self.esp.config[name]["limit_on"]            

    #         self.timer.deinit()
    #         self.esp.deallocate_timer(self.timer_id)
    #         self.timer = None

    #         print(f"{self.name}_MOV_MIN")

    # def on_min(self):

    #     if self.esp.pcf.pin(self.min_id) == self.esp.config[name]["limit_on"]::            

    #         self.timer.deinit()
    #         self.esp.deallocate_timer(self.timer_id)
    #         self.timer = None

    #         print(f"{self.name}_MOV_MIN")

    # def get_position(self):

    #     if self.n_toggle % 2 == 0:
    #         position = self.n_toggle // 2
    #     else:
    #         position =  self.n_toggle // 2 + 1
    #     print(position)

    # def set_position(self, new_position, freq):

    #     new_position = int(new_position)
    #     if self.n_toggle % 2 == 0:
    #         old_position = self.n_toggle // 2
    #     else:
    #         old_position =  self.n_toggle // 2 + 1

    #     nsteps = new_position - old_position
    #     self.move(nsteps, freq)
    
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