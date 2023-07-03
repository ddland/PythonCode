from mpmulticore import CoreTask
import machine
import time
import _thread
import utime

import motor_step_28BYJ as motor


class BlinkLED():
    def __init__(self):
        self.r = machine.PWM(machine.Pin(12))
        self.b = machine.PWM(machine.Pin(11))
        self.g = machine.PWM(machine.Pin(10))
        self.state_r = False
        self.step = motor.Stepper28BYJ([0, 1, 2, 3], steps='half')

    def on(self):
        self.r.duty_u16(65025)
        self.step.run(8038)
    
    def off(self):
        self.r.duty_u16(0)
        
    def toggle(self):
        if self.state_r == False:
            self.on()
            self.state_r == True
        else:
            self.off()
            self.state_r == False

if __name__ == "__main__":
    ldr = machine.ADC(machine.Pin(26))
    leds = BlinkLED()

    def task(arg):
        led = arg[0]
        ldr = arg[1]
        ldr_v = ldr.read_u16()
        print(ldr_v)
        if ldr_v > 30000:
            led.on()
        else:
            led.off()
            
    def cleanup():
        pass
    
    core1 = CoreTask(task, [leds, ldr], cleanup)
    core1.enable()
    _thread.start_new_thread(core1.core_task, ())
    run = True
    while run:
        try:
            utime.sleep(0.1)
        except KeyboardInterrupt:
            core1.shutdown()
            run = False
    