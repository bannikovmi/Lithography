from ESP.tasks import PeriodicTask
from machine import Timer

class Movement(PeriodicTask):

    def __init__(self, name, drive, nsteps=1):

        super().__init__(name=name, freq=drive._speed)
        
        # Save drive and nsteps to attributes, calculate single step and initialize step counter
        self.drive = drive
        self.nsteps = abs(nsteps)
        self.single_step = 256 // self.drive._msres * self.drive.direction()
        self.counter = 0

        if nsteps > 0:             
            
            if self.drive.max_en: # if max limit switcher detection is on
                
                # Ensure drive is not at max limit
                if (self.drive.max_pin.value() == self.drive.config["limit_on"]):
                    raise Exception(f"{self.name}_MAX")
                # Attach interrupt
                self.drive.max_pin.irq(trigger=self.drive.limit_trigger, handler=self.on_limit_trigger)

            # Set direction sign
            self.drive.direction(1)
        
        else:    

            if self.drive.min_en: # if min limit switcher detection is on
                
                # Ensure drive is not at min limit
                if (self.drive.min_pin.value() == self.drive.config["limit_on"]):
                    raise Exception(f"{self.name}_MIN")
                # Attach interrupt
                self.drive.min_pin.irq(trigger=self.drive.limit_trigger, handler=self.on_limit_trigger)

            # Set direction sign
            self.drive.direction(-1)

#         init_val = not self.drive.esp.config[self.drive.name]["limit_on"]
#         self.interrupt = MovementInterrupt(int_name, int_id, init_val)

    def callback(self, t):

        # print(f"{self.name} callback {self.counter}")

        if self.counter < self.nsteps:
            self.counter += 1
            self.drive.config["pos"] += self.single_step
            self.drive.step_pin(not self.drive.step_pin()) # Toggle step pin
        else:
            self.finished = True
            print(f"{self.drive.name}_MOV_FIN")

    def finish(self):
        
        self.drive.update_config()
        self.drive.dump_config()
        
    def on_limit_trigger(self, pin):
        
        self.drive.esp.task_manager.abort_task(self.name)
        pin.irq(handler=None)
        
        if pin == self.drive.max_pin:
            print(f"{self.name}_MAX")
        else:
            print(f"{self.name}_MIN")
