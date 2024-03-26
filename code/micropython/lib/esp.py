import sys, time
from machine import ADC, Pin

# local imports
from resource import Resource

class ESP(Resource):

	blink_id = 2
	HIGH = 1
	LOW = 0

	esp_commands = {
		"AD": "get_adc_value",
		"BL": "blink",
		"GP": "get_pin_state",
		"SP": "set_pin_state",
		"TP": "toggle_pin_state",
	}

	# merge with parent commands
	available_commands = Resource.available_commands | esp_commands

	def __init__(self):
		
		super().__init__()
		self.timers_pool = [False, False, False, False]

	def blink(self, sleep_time):

		blink_pin = Pin(self.blink_id, Pin.OUT)
		blink_pin.on()
		time.sleep_ms(int(sleep_time))
		blink_pin.off()

	def get_adc_value(self, adc_id):

		self.send_message(ADC(int(adc_id)).read())

	def get_pin_state(self, pin_id):

		pin = Pin(int(pin_id))
		self.send_message(pin.value())

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
			self.send_message("no_available_timers")


	def deallocate_timer(self, timer_id):

		self.timers_pool[timer_id] = False
