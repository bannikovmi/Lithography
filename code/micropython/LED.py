from machine import Pin, PWM

# local imports
from resource import Resource

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

        self.pwm = PWM(Pin(self.esp.config[self.name]["pin_id"]))
        
        # Set parametres to default values
        self.duty = self.esp.config[self.name]["duty"]
        self.freq = self.esp.config[self.name]["freq"]

    
    def duty(self, value=None):
        if value is None:
            print(self.pwm.duty())
        else:
            self.pwm.duty(int(value))

    def freq(self, value=None):
        if value is None:
            print(self.pwm.freq())
        else:
            self.pwm.freq(int(value))
