from dht import DHT22
from machine import Pin

from resource import Resource

class DHT(Resource):

    DHT_commands = {
        "MS": "measure",
        "MH": "measure_humidity",
        "MT": "measure_temperature",
        "GH": "get_humidity",
        "GT": "get_temperature"
    }

    # merge with parent commands
    available_commands = Resource.available_commands | DHT_commands

    def __init__(self, esp, bus_id):
        self.esp = esp
        self.bus_id = bus_id
        self.device = DHT22(Pin(bus_id))

    def measure(self):
        self.device.measure()

    def measure_humidity(self):
        self.device.measure()
        print(self.device.humidity())

    def measure_temperature(self):
        self.device.measure()
        print(self.device.temperature())

    def get_temperature(self):
        print(self.device.temperature())

    def get_humidity(self):
        print(self.device.humidity())