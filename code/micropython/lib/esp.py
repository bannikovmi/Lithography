import json, sys, time
from machine import ADC, SoftI2C, Pin, PWM, Timer

# local imports
from resource import Resource
from PCF import PCF

class ESP(Resource):

    esp_commands = {
        "AD": "get_adc_value",
        "BL": "blink",
        "DP": "deinit_pwm",
        "GP": "get_pin_state",
        "IP": "initialize_pin",
        "PP": "pcf_pin",
        "PW": "init_pwm",
        "SP": "set_pin_state",
        "TP": "toggle_pin_state",
        "UC": "update_config",
    }

    pin_states = {
        "HIGH": 1,
        "LOW": 0
    }

    pin_modes = {
        "IN": Pin.IN,
        "OUT": Pin.OUT,
        "OD": Pin.OPEN_DRAIN,
        "NO": None,
    }

    pull_modes = {
        "UP": Pin.PULL_UP,
        "DOWN": Pin.PULL_DOWN,
        "NO": None,
    }

    trigger_modes = {
        "RISE": Pin.IRQ_RISING,
        "FALL": Pin.IRQ_FALLING
    }

    # merge with parent commands
    available_commands = Resource.available_commands | esp_commands

    def __init__(self, config_file):
        
        super().__init__()
        
        self.timers_pool = [False, False, False, False]
        self.adc_timer = None
        self.config_file = config_file

        with open(self.config_file, "r") as file:
            self.config = json.load(file)

        # Initialize I2C communication
        scl_pin = Pin(self.config["ESP"]["scl_id"])
        sda_pin = Pin(self.config["ESP"]["sda_id"])
        self.i2c = SoftI2C(freq=400000, sda=sda_pin, scl=scl_pin)
        self.pcf = PCF(self.i2c, 0x20)

        # # Attach interrupt to int pin
        self.int_pin = Pin(self.config["ESP"]["int_id"], Pin.IN, Pin.PULL_UP)
        self.int_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.on_pcf_int)

    def on_pcf_int(self, p): 
        

    def blink(self, sleep_time):

        blink_pin = Pin(self.blink_id, Pin.OUT)
        blink_pin.on()
        time.sleep_ms(int(sleep_time))
        blink_pin.off()

    def deinit_pwm(self, pin_id):
        
        pin = Pin(int(pin_id))
        pwm = PWM(pin)
        pwm.deinit()

    def get_adc_value(self, adc_id, ntimes=None, freq=None):

        if adc_id == "STOP":
            if self.adc_timer is not None:
                self.adc_timer.deinit()
                self.timers_pool[self.adc_timer_id] = False
                self.adc_timer = None
        else:
            if ntimes is None:
                self.send_message(f"ESP_AD_{adc_id}_{ADC(int(adc_id)).read()}")
            else:   
                if self.adc_timer is None:
                    
                    self.adc_id = adc_id
                    self.adc_counter = 0
                    self.adc_nsteps = int(ntimes)
                    self.adc_pin = ADC(int(adc_id))

                    self.adc_timer_id = self.allocate_timer_id()
                    self.adc_timer = Timer(self.adc_timer_id)
                    self.adc_timer.init(mode=Timer.PERIODIC, freq=int(freq),
                        callback=lambda t: self.on_adc_timer_event())
                
                else:
                    print("ESP_AD_BUSY")

    def pcf_pin(self, pin_id, state=None):

        if state is None:
            print(self.pcf.pin(int(pin_id)))
        else:
            self.pcf.pin(int(pin_id), int(state))

    def get_pin_state(self, pin_id):

        pin = Pin(int(pin_id))
        self.send_message(pin.value())

    def initialize_pin(self, pin_id, mode, pull):
        
        return Pin(int(pin_id), mode=self.pin_modes[mode], pull=self.pull_modes[pull])
        
    def init_pwm(self, pin_id, freq=1000, duty=512):
        
        pin = Pin(int(pin_id))
        pwm = PWM(pin)
        pwm.freq(int(freq))
        pwm.duty(int(duty))
        
    def set_pin_state(self, pin_id, state):

        pin = Pin(int(pin_id), Pin.OUT)
        pin.value(int(state))

    def toggle_pin_state(self, pin_id):

        pin = Pin(int(pin_id), Pin.OUT)
        pin.value(not pin.value())

    def allocate_timer_id(self):

        # dynamically allocate timer to a task
        try:
            timer_id = self.timers_pool.index(False)
            self.timers_pool[timer_id] = True
            timer = Timer(timer_id)
            timer.init(mode=Timer.PERIODIC, freq=int(self.speed()),
                    callback=lambda t: self.on_timer_event())
            return timer
        except ValueError:
            print("no_available_timers")

    def deallocate_timer(self, timer_id):

        self.timers_pool[timer_id] = False

    def attach_interrupt(self, pin_id, trigger, handler):
        
        Pin(pin_id, Pin.IN).irq(trigger=self.trigger_modes[trigger], handler=handler)

    def detach_interrupt(self, pin_id):
        
        Pin(pin_id, Pin.IN).irq(handler=None)

    def on_adc_timer_event(self):

        if self.adc_counter < self.adc_nsteps:
            self.adc_counter += 1
            self.send_message(f"ESP_AD_{self.adc_id}_{self.adc_pin.read()}")
        else:
            if self.adc_timer is not None:
                self.adc_timer.deinit()
                self.timers_pool[self.adc_timer_id] = False
                self.adc_timer = None

    def update_config(self):

        with open(self.config_file, "w"):
            json.dump(self.config, self.config_file)
