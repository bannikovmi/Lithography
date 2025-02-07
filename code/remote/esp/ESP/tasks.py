from machine import Timer, Pin

class TaskManager:

    timers_pool = [False, False, False, False]
    interrupts = {}
    tasks = {}

    def __init__(self, esp):

        self.esp = esp

    def start_task(self, task):
        
        # print("starting task")

        if task.name in self.tasks: # Task is already performing
            print(f"TMG_{task.name}_DUP")
            return

        timer_id = self.allocate_timer_id()
        if timer_id is None: # Timer failed to allocate
            return

        if timer_id is not None:

            # print("init timer")

            if task.interrupt is not None: # Add interrupt to pool
                
                # print("attaching interrupt")
                
                # Attach esp interrupt if not yet attached
                # print("old interrupt list", self.interrupts)
                if bool(self.interrupts) == False:

                    # print("emtpy interrupt list")
                    pin_id = self.esp.config["ids"]["int"]
                    Pin(pin_id, Pin.IN).irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                        handler=self.int_handler)

                self.interrupts[task.name] = task.interrupt
                # print("new interrupt list", self.interrupts)

            # print("about to start timer")

            self.tasks[task.name] = task
            task.timer_id = timer_id
            task.timer = Timer(task.timer_id)
            task.timer.init(mode=task.mode, freq=task.freq,
                callback=lambda t: self.callback_wrapper(task, t))

    def abort_task(self, name):

        # print("aborting task")

        try:
            
            task = self.tasks[name]
            task.finish()
            task.timer.deinit()
            self.deallocate_timer_id(task.timer_id)
            del self.tasks[name]
            del self.interrupts[name]

            # Detach ESP interrupt if no interrupts are left
            if bool(self.interrupts) == False:
                pin_id = self.esp.config["ids"]["int"]
                Pin(pin_id, Pin.IN).irq(handler=None)

        except KeyError: # task is not running
            pass

    def callback_wrapper(self, task, t):

        # print(f"in callback wrapper of {task.name}")

        if task.finished:
            # print(f"{task.name} is finished")
            task.finish()
            task.timer.deinit()
            self.deallocate_timer_id(task.timer_id)

            # Multiple timeouts may occur after task.finished is set to True,
            # Thus we make sure task and interrupt are deleted only once
            try: 
                del self.tasks[task.name]
                del self.interrupts[task.name]
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

    def int_handler(self, pin):

        pass
        # for name in self.interrupts:
            
        #     new_value = self.esp.pcf.pin(self.interrupts[name].int_id)
        #     old_value = self.interrupts[name].init_val

        #     # print(f"\tname: {name},\tnew_value: {new_value},\told_value: {old_value}")
        #     if new_value != old_value:
        #         # print(f"{self.interrupts[name].name}")
        #         self.abort_task(name)

class LastingTask:

    def __init__(self, name, mode, freq):

        self.name = name
        self.mode = mode
        self.freq = freq

        self.finished = False
        self.interrupt = None

    def callback(self, t):
        # Overwrite in child classes
        pass 

    def finish(self):
        # Overwrite in child classes
        pass
