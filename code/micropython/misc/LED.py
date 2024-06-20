from machine import Pin, PWM

# local imports
from resource.resource import Resource

class LED(Resource):

    LED_commands = {
        "DUT": "duty",
        "FRQ": "freq",
    }

    # merge with parent commands
    available_commands = Resource.available_commands | LED_commands

    def __init__(self, esp, name):

        self.esp = esp
        self.name = name

        self.pwm = PWM(Pin(self.esp.config[self.name]["pin_id"]),
            duty=self.esp.config[self.name]["duty"], 
            freq=self.esp.config[self.name]["freq"])
    
    def duty(self, value=None):
        if value is None:
            print(f"{self.name}_DUT_{self.pwm.duty()}")
        else:
            self.pwm.duty(int(value))

    def freq(self, value=None):
        if value is None:
            print(f"{self.name}_FRQ_{self.pwm.freq()}")
        else:
            self.pwm.freq(int(value))
