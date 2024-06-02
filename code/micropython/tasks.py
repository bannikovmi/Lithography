from machine import Timer

class TaskManager:

    timers_pool = [False, False, False, False]
    tasks = {}

    def start_task(self, task):
        
        if task.name in self.tasks: # Task is already performing
            print(f"TMG_{task.name}_DUP")
            return

        timer_id = self.allocate_timer_id()
        if timer_id is None:
            return

        if timer_id is not None:

            self.tasks[task.name] = task
            task.timer_id = timer_id
            task.timer = Timer(task.timer_id)
            task.timer.init(mode=task.mode, freq=task.freq,
                callback=lambda t: self.callback_wrapper(task, t))

    def abort_task(self, name):

        try:
            task = self.tasks[name]
            task.timer.deinit()
            self.deallocate_timer_id(task.timer_id)
            del self.tasks[name]
        except KeyError: # task is not running
            pass

    def callback_wrapper(self, task, t):

        if task.finished:
            task.timer.deinit()
            self.deallocate_timer_id(task.timer_id)

            # Multiple timeouts may occur after task.finished is set to True,
            # Thus we make sure task is deleted only once
            try: 
                del self.tasks[task.name]
            except KeyError:
                pass
        else:
            task.callback(t)

    def allocate_timer_id(self):

        try:
            timer_id = self.timers_pool.index(False)
        except ValueError:
            print("TMG_BUSY")
            return None

        self.timers_pool[timer_id] = True
        return timer_id

    def deallocate_timer_id(self, timer_id):

        self.timers_pool[timer_id] = False

class LastingTask:

    def __init__(self, name, mode, freq):

        self.name = name
        self.mode = mode
        self.freq = freq

        self.finished = False

    def callback(self, t):
        # Overwrite in child classes
        pass 
        

