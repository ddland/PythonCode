import _thread
import utime
import machine

class CoreTask():
    def __init__(self, task, arg, cleanup):
        self._running = False
        self._shutdown = False
        self._clean = False
        self.task = task
        self.arg = arg
        self.cleanup = cleanup
        
    def core_task(self):
        while not self._shutdown:
            while self._running and not self._shutdown:
                self.task(self.arg)
                utime.sleep(0.5)
            utime.sleep(0.5)
            if self._clean:
                self.cleanup()
                self._clean = False
            
    def enable(self):
        self._running = True
        
    def disable(self):
        self._running = False
        self._clean = True
        
    def shutdown(self):
        print('bye bye')
        self.disable()
        self._shutdown = True


if __name__ == "__main__":
    def cleanup():
        print('cleaning...')

    def print_msg(msg):
        print(utime.time(), msg)
    
    core1 = CoreTask(print_msg, ['hello'], cleanup)
    _thread.start_new_thread(core1.core_task, ())

    for i in range(3):
        core1.enable()
        utime.sleep(1)
        core1.disable()
        utime.sleep(2)
        core1.enable()
        utime.sleep(3)
        core1.disable()
    core1.shutdown()
    