from machine import Timer

class TaskManager:
	
	timers_pool = [False, False, False, False]

	def __init__(self):
		pass

	def run(self, task):
		task.timer.init(mode=task.mode, freq=task.freq, callback=task.callback)

	def allocate_timer_id(self):

        try:
            timer_id = self.timers_pool.index(False)
        except ValueError:
            print("TMG_TIM_BUSY")
            return None

        self.timers_pool[timer_id] = True
        return timer_id

    def deallocate_timer_id(self, timer_id):

    	self.timers_pool[timer_id] = False

class LastingTask:

	def __init__(self, timer, mode, freq):

		self.timer = timer
		self.mode = mode
		self.freq = freq

	def callback(self, timer):
		# Overwrite in child classes
		pass

