import sys, time
from machine import ADC, Pin, Timer

# local imports
from resource import Resource

class ESP(Resource):

	blink_id = 2

	esp_commands = {
		"AD": "get_adc_value",
		"BL": "blink",
		"GP": "get_pin_state",
		"IP": "initialize_pin",
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

		with open(self.config_file, "r") as file:
			self.config = json.load(file)

	def blink(self, sleep_time):

		blink_pin = Pin(self.blink_id, Pin.OUT)
		blink_pin.on()
		time.sleep_ms(int(sleep_time))
		blink_pin.off()

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


	def get_pin_state(self, pin_id):

		pin = Pin(int(pin_id))
		self.send_message(pin.value())

	def initialize_pin(self, pin_id, mode, pull):
		
		return Pin(int(pin_id), mode=self.pin_modes[mode], pull=self.pull_modes[pull])
		
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
			return timer_id
		except ValueError:
			print("no_available_timers")

	def deallocate_timer(self, timer_id):

		self.timers_pool[timer_id] = False

	def attach_interrupt(self, pin_id, trigger, handler):
		Pin(pin_id, Pin.IN).irq(trigger = self.trigger_modes[trigger], handler=handler)

	def detach_interrupt(sefl, pin_id):
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
