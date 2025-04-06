from aht.ahtx0 import AHT20
from machine import Pin

from resource.resource import Resource

class AHT(Resource):

    AHT_commands = {
        "GTH": "get_humidity",
        "GTT": "get_temperature",
        "GTM": "get_measurements"
    }

    # merge with parent commands
    available_commands = Resource.available_commands | AHT_commands

    def __init__(self, esp, name):

        self.device = AHT20(esp.i2c)

    def get_temperature(self):
        print(f"AHT_GTT_{self.device.temperature}")

    def get_humidity(self):
        print(f"AHT_GTH_{self.device.relative_humidity}")

    def get_measurements(self):
        print(f"AHT_GTM_{self.device.temperature}_{self.device.relative_humidity}")