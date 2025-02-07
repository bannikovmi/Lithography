import json, sys, time
from machine import ADC, SoftI2C, Pin, PWM, Timer

# local imports
from resource.resource import Resource
from ESP.tasks import TaskManager
from ESP.PCF import PCF
from tmc.uart import TMC_UART

class ESP(Resource):

    esp_commands = {
        "PCF": "PCF_pin",
        "INT": "INT"
    }

    # merge with parent commands
    available_commands = Resource.available_commands | esp_commands

    def __init__(self):
        
        super().__init__(name="ESP")

        # Create TaskManager
        self.task_manager = TaskManager(self)

        # Initialize I2C communication
        scl_pin = Pin(self.config["ids"]["scl"])
        sda_pin = Pin(self.config["ids"]["sda"])
        self.i2c = SoftI2C(freq=400000, sda=sda_pin, scl=scl_pin)
        self.pcf = PCF(self.i2c, 0x20)

        # Initialize UART communication with TMC drives
        self.tmc_uart = TMC_UART(self.config["UART"])

        # # Attach interrupt to int pin
        # self.int_pin = Pin(self.config["ESP"]["int_id"], Pin.IN, Pin.PULL_UP)
        # self.int_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.on_pcf_int)

    def PCF_pin(self, pin_id, state=None):

        pin_id = int(pin_id)
        name = f"ESP_PCF_{pin_id}"

        if state is None:
            pin_state = int(self.pcf.pin(pin_id))
            print(f"{name}_{pin_state}")
            return pin_state
        else:
            self.pcf.pin(pin_id, int(state))

    def INT(self):

        for name in self.task_manager.interrupts:
            interrupt = self.task_manager.interrupts[name]
            print(name, interrupt.name, interrupt.int_id, interrupt.init_val)
