from machine import Pin

# local imports
from resource.resource import Resource

class Switch(Resource):

    LED_commands = {
        "TGL": "toggle",
        "STE": "state",
    }

    # merge with parent  commands
    available_commands = Resource.available_commands | LED_commands

    def __init__(self, esp, name):

        self.esp = esp
        self.name = name

        self.pin = Pin(self.esp.config[name]["pin_id"])
        self.btn = Pin(self.esp.config[name]["btn_id"])

        # Set state to default
        self.state(self.esp.config[name]["on_startup"])

    def state(self, value=None):
        if value is None:
            print(self.pin.value())
        else:
            self.pin.value(int(value))

    def toggle(self):
        self.pin.value(int(not self.state()))
