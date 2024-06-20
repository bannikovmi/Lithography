import json, sys, time
from machine import ADC, SoftI2C, Pin, PWM, Timer

# local imports
from resource.resource import Resource
from ESP.tasks import TaskManager
from ESP.ADCReader import ADCReader
from ESP.PCF import PCF
from tmc.uart import TMC_UART

class ESP(Resource):

    esp_commands = {
        "ADC": "ADC_read",
        "PCF": "PCF_pin",
        "INT": "INT"
    }

    # merge with parent commands
    available_commands = Resource.available_commands | esp_commands

    def __init__(self, config_file):
        
        super().__init__()
        
        self.config_file = config_file
        with open(self.config_file, "r") as file:
            self.config = json.load(file)

        # Create TaskManager
        self.task_manager = TaskManager(self)

        # Initialize I2C communication
        scl_pin = Pin(self.config["ESP"]["scl_id"])
        sda_pin = Pin(self.config["ESP"]["sda_id"])
        self.i2c = SoftI2C(freq=400000, sda=sda_pin, scl=scl_pin)
        self.pcf = PCF(self.i2c, 0x20)

        # Initialize UART communication with TMC drives
        self.tmc_uart = TMC_UART(self.config)

        # # Attach interrupt to int pin
        # self.int_pin = Pin(self.config["ESP"]["int_id"], Pin.IN, Pin.PULL_UP)
        # self.int_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.on_pcf_int)

    def ADC_read(self, adc_id, freq=1000, nsteps=1):

        name = f"ESP_ADC_{adc_id}"

        if freq == "ABT":
            self.task_manager.abort_task(name)
        else:
            adc_reader = ADCReader(name, int(adc_id), int(freq), int(nsteps))
            self.task_manager.start_task(adc_reader)

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

    # def blink(self, sleep_time):

    #     blink_pin = Pin(self.blink_id, Pin.OUT)
    #     blink_pin.on()
    #     time.sleep_ms(int(sleep_time))
    #     blink_pin.off()

    # def deinit_pwm(self, pin_id):
        
    #     pin = Pin(int(pin_id))
    #     pwm = PWM(pin)
    #     pwm.deinit()

    # def get_adc_value(self, adc_id, ntimes=None, freq=None):

    #     if adc_id == "STOP":
    #         if self.adc_timer is not None:
    #             self.adc_timer.deinit()
    #             self.timers_pool[self.adc_timer_id] = False
    #             self.adc_timer = None
    #     else:
    #         if ntimes is None:
    #             self.send_message(f"ESP_AD_{adc_id}_{ADC(int(adc_id)).read()}")
    #         else:   
    #             if self.adc_timer is None:
                    
    #                 self.adc_id = adc_id
    #                 self.adc_counter = 0
    #                 self.adc_nsteps = int(ntimes)
    #                 self.adc_pin = ADC(int(adc_id))

    #                 self.adc_timer_id = self.allocate_timer_id()
    #                 self.adc_timer = Timer(self.adc_timer_id)
    #                 self.adc_timer.init(mode=Timer.PERIODIC, freq=int(freq),
    #                     callback=lambda t: self.on_adc_timer_event())
                
    #             else:
    #                 print("ESP_AD_BUSY")

    # def pcf_pin(self, pin_id, state=None):

    #     if state is None:
    #         print(self.pcf.pin(int(pin_id)))
    #     else:
    #         self.pcf.pin(int(pin_id), int(state))

    # def get_pin_state(self, pin_id):

    #     pin = Pin(int(pin_id))
    #     self.send_message(pin.value())

    # def initialize_pin(self, pin_id, mode, pull):
        
    #     return Pin(int(pin_id), mode=self.pin_modes[mode], pull=self.pull_modes[pull])
        
    # def init_pwm(self, pin_id, freq=1000, duty=512):
        
    #     pin = Pin(int(pin_id))
    #     pwm = PWM(pin)
    #     pwm.freq(int(freq))
    #     pwm.duty(int(duty))
        
    # def set_pin_state(self, pin_id, state):

    #     pin = Pin(int(pin_id), Pin.OUT)
    #     pin.value(int(state))

    # def toggle_pin_state(self, pin_id):

    #     pin = Pin(int(pin_id), Pin.OUT)
    #     pin.value(not pin.value())

    # def allocate_timer_id(self):

    #     # dynamically allocate timer to a task
    #     try:
    #         timer_id = self.timers_pool.index(False)
    #         self.timers_pool[timer_id] = True
    #         timer = Timer(timer_id)
    #         timer.init(mode=Timer.PERIODIC, freq=int(self.speed()),
    #                 callback=lambda t: self.on_timer_event())
    #         return timer
    #     except ValueError:
    #         print("no_available_timers")

    # def deallocate_timer(self, timer_id):

    #     self.timers_pool[timer_id] = False

    # def attach_interrupt(self, pin_id, trigger, handler):
        
    #     Pin(pin_id, Pin.IN).irq(trigger=self.trigger_modes[trigger], handler=handler)

    # def detach_interrupt(self, pin_id):
        
    #     Pin(pin_id, Pin.IN).irq(handler=None)

    # def on_adc_timer_event(self):

    #     if self.adc_counter < self.adc_nsteps:
    #         self.adc_counter += 1
    #         self.send_message(f"ESP_AD_{self.adc_id}_{self.adc_pin.read()}")
    #     else:
    #         if self.adc_timer is not None:
    #             self.adc_timer.deinit()
    #             self.timers_pool[self.adc_timer_id] = False
    #             self.adc_timer = None

    # def update_config(self):

    #     with open(self.config_file, "w"):
    #         json.dump(self.config, self.config_file)
