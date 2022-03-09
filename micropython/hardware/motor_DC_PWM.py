# mosfet + motor

import machine
import time

motor = machine.PWM(machine.Pin(20))

motor.freq(1000)

for duty in range(65025):
    motor.duty_u16(duty)
    time.sleep(0.0001)
time.sleep(2)
for duty in range(65025,0,-1):
    motor.duty_u16(duty)
    time.sleep(0.0001)