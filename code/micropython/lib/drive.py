from machine import Timer

# local imports
from resource import Resource

class Drive(Resource):

    POS = 1
    NEG = 0

    drive_commands = {
        "DS": "disable",
        "EN": "enable",
        "GP": "get_position",
        "MV": "move",
        "SP": "set_position"
    }

    # merge with parent commands
    available_commands = Resource.available_commands | drive_commands

    def __init__(self, esp, name, en_id, dir_id, step_id, min_id, max_id):
    
        # Save esp resource instance and name
        self.esp = esp
        self.name = name

        # Save pin identifiers
        self.en_id = en_id
        self.dir_id = dir_id
        self.step_id = step_id
        self.min_id = min_id
        self.max_id = max_id

        # Initialize on_startup_parametres
        self.n_toggle = 0
        self.direction = 0
        self.timer = None

        # Attach pull resistors
        self.esp.initialize_pin(self.min_id, mode="IN", pull="UP")
        self.esp.initialize_pin(self.max_id, mode="IN", pull="UP")

    def disable(self):
        # setting value to HIGH disables pin
        self.esp.set_pin_state(self.en_id, 1)

    def enable(self):
        # setting value to LOW enables pin
        self.esp.set_pin_state(self.en_id, 0)

    def get_position(self):

        if self.n_toggle % 2 == 0:
            position = self.n_toggle // 2
        else:
            position =  self.n_toggle // 2 + 1
        print(position)

    def set_position(self, new_position, freq):

        new_position = int(new_position)
        if self.n_toggle % 2 == 0:
            old_position = self.n_toggle // 2
        else:
            old_position =  self.n_toggle // 2 + 1

        nsteps = new_position - old_position
        self.move(nsteps, freq)

    def move(self, nsteps, freq):

        # Ensure that a move operation is not already in place
        if self.timer is None:

            # Save nsteps value, calculate direction and single_toggle values, attach interrupts
            self.nsteps = int(nsteps)
            
            if self.nsteps > 0:

                # Check that the sensor is not currently at max
                if self.esp.config[f"{self.name}"]["is_at_max"]:
                    print(f"{self.name}_MV_MAX")
                else:
                    self.direction = self.POS
                    self.single_toggle = 1
                    self.esp.attach_interrupt(self.max_id, trigger="FALL", handler=self.on_max_event)
            
            else:

                # Check that we are not at min
                if self.esp.config[f"{self.name}"]["is_at_min"]:
                    print(f"{self.name}_MV_MIN")
                else:
                    self.direction = self.NEG
                    self.single_toggle = -1
                    self.esp.attach_interrupt(self.min_id, trigger="FALL", handler=self.on_max_event)


            # Perform this calculation here and not in the callback
            self.double_nsteps = 2*abs(self.nsteps)
            self.counter = 0

            # Initialize pins state
            self.esp.set_pin_state(self.dir_id, self.direction)
            self.esp.set_pin_state(self.step_id, 0)

            # Initialize timer
            self.timer_id = self.esp.allocate_timer_id()
            self.timer = Timer(self.timer_id)
            self.timer.init(mode=Timer.PERIODIC, freq=2*int(freq),
                callback=lambda t: self.on_timer_event())

        else:
            print(f"{self.name}_MV_BUSY")
        
    def on_timer_event(self):

        if self.counter < self.double_nsteps: # frequency is two-fold
            self.esp.toggle_pin_state(self.step_id)
            self.counter += 1
            self.n_toggle += self.single_toggle
        else:
            if self.timer is not None:
                self.timer.deinit()
                self.esp.deallocate_timer(self.timer_id)
                self.timer = None
                print(f"{self.name}_MV_END")

    def on_min_event(self, min_id):

        if self.timer is not None:

            self.esp.detach_interrupt(min_id)
            self.config[f"{self.name}"]["is_at_min"] = True

            self.timer.deinit()
            self.esp.deallocate_timer(self.timer_id)
            self.timer = None

            print(f"{self.name}_MV_MIN")

    def on_max_event(self, max_id):

        if self.timer is not None:

            self.esp.detach_interrupt(max_id)
            self.config[f"{self.name}"]["is_at_max"] = True

            self.timer.deinit()
            self.esp.deallocate_timer(self.timer_id)
            self.timer = None

            print(f"{self.name}_MV_MAX")


