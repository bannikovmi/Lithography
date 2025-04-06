from machine import Pin, PWM, Timer

# local imports
from resource.resource import Resource
from ESP.tasks import OneShotTask

class LED(Resource):

    LED_commands = {
        "DUT": "duty",
        "FRQ": "freq",
        "ILM": "illuminate",
    }

    # merge with parent commands
    available_commands = Resource.available_commands | LED_commands

    def __init__(self, esp, name):

        self.esp = esp
        self.config = esp.config[name]
        self.name = name
        self.pwm = PWM(Pin(self.config["pin_id"]), duty=self.config["duty"], freq=self.config["freq"])
        
        self.duty(self.config["duty"])
        self.freq(self.config["freq"])
    
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
            
    def illuminate(self, time=None, duty=None):

        name = f"{self.name}_ILM"

        if time == "ABT":
            self.esp.task_manager.abort_task(name)
        else:
            try:
                illumination = Illumination(name=name, led=self, time=int(time), duty=int(duty))
                self.esp.task_manager.start_task(illumination)
            except Exception as e:
                print(e)
            
class Illumination(OneShotTask):
    
    def __init__(self, name, led, time, duty):

        super().__init__(name=name, period=time)
        
        # Save led and duty to attributes
        self.led = led
        self.duty = duty
    
    def on_start(self):
        
        self.led.duty(self.duty)
    
    def callback(self, t):

        self.led.duty(0)
        print(f"{self.name}_FIN")

