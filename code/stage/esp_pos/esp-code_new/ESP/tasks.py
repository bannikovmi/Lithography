from machine import Timer, Pin

class TaskManager:

    timers_pool = [False, False, False, False]
    tasks = {}

    def __init__(self, esp):

        self.esp = esp

    def start_task(self, task):

        if task.name in self.tasks: # Task is already performing
            print(f"TMG_{task.name}_DUP")
            return

        timer_id = self.allocate_timer_id()
        if timer_id is None: # Timer failed to allocate
            return

        if timer_id is not None:

            self.tasks[task.name] = task
            task.timer_id = timer_id
            task.timer = Timer(task.timer_id)
            
            if task.mode == Timer.PERIODIC:
                task.timer.init(mode=task.mode, freq=task.freq,
                    callback=lambda t: self.periodic_wrapper(task, t))
            else:
                task.timer.init(mode=task.mode, period=task.period,
                    callback=lambda t: self.one_shot_wrapper(task, t))
            task.on_start()

    def abort_task(self, name):

        try:
            
            task = self.tasks[name]
            task.finish()
            task.timer.deinit()
            self.deallocate_timer_id(task.timer_id)
            del self.tasks[name]

        except KeyError: # task is not running or is deleted already
            pass

    def periodic_wrapper(self, task, t):

        if task.finished:
    
            task.finish()
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
            
    def one_shot_wrapper(self, task, t):
        
        task.callback(t)
        task.finish()
        task.timer.deinit()
        self.deallocate_timer_id(task.timer_id)
        
        try: 
            del self.tasks[task.name]
        except KeyError:
            pass
        

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

class Task:
    
    def __init__(self, name):
        
        self.name = name
        self.finished = False

    def on_start(self):
        # Overwrite in child classes
        pass

    def callback(self, t):
        # Overwrite in child classes
        pass

    def finish(self):
        # Overwrite in child classes
        pass

class PeriodicTask(Task):

    mode = Timer.PERIODIC

    def __init__(self, name, freq):

        super().__init__(name)
        self.freq = freq

class OneShotTask(Task):
    
    mode = Timer.ONE_SHOT
    
    def __init__(self, name, period):
        
        super().__init__(name)
        self.period = period
        