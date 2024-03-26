# clockwise = 1
# counterclockwise = 0
# steps_per_revolution = 

class MotionMessage():

	def __init__(self, direction=1, nsteps=1, delay=1):
		self.direction = direction
		self.nsteps = nsteps
		self.delay = delay

	def to_serial_message(self):
		return f"{self.direction} {self.nsteps} {self.delay}\n"