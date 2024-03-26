from machine import Timer

# local imports
from resource import Resource

class Drive(Resource):

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
    
        # save esp resource instance
        self.esp = esp
        self.name = name

        # save pin identifiers
        self.en_id = en_id
        self.dir_id = dir_id
        self.step_id = step_id
        self.min_id = min_id
        self.max_id = max_id

        # on_startup_parametres
        self.position = 0.0
        self.direction = 0
        self.timer = None

    def disable(self):
        # setting value to HIGH disables pin
        self.esp.set_pin_state(self.en_id, self.esp.HIGH)

    def enable(self):
        # setting value to LOW enables pin
        self.esp.set_pin_state(self.en_id, self.esp.LOW)

    def get_position(self):
        print(int(self.position))

    def set_position(self, new_position, freq):

        new_position = int(new_position)
        if new_position > self.position:
            direction = 1
        else:
            direction = 0

        nsteps = abs(new_position - self.position)
        self.move(direction, nsteps, freq)

    def move(self, direction, nsteps, freq):

        # Ensure that a move operation is not already in place
        if self.timer is None:

            # save nsteps value
            self.nsteps = int(nsteps)
            self.direction = bool(int(direction))

            self.esp.set_pin_state(self.dir_id, self.direction)

            self.timer_id = self.esp.allocate_timer_id()
            self.timer = Timer(self.timer_id)
            self.counter = 0
            self.timer.init(mode=Timer.PERIODIC, freq=2*int(freq),
                callback=lambda t: self.on_timer_event())

        else:
            print(f"{self.name}_MV_BUSY")
        
    def on_timer_event(self):

        if self.counter < 2*self.nsteps: # frequency is two-fold
            self.esp.toggle_pin_state(self.step_id)
            self.counter += 1
            self.position -= 0.5*(-1)**self.direction
        else:
            self.timer.deinit()
            self.esp.deallocate_timer(self.timer_id)
            self.timer = None
            print(f"{self.name}_MV_END")
