import machine
import time

motor = machine.Pin(20, machine.Pin.OUT)

motor.high()
time.sleep(2)
motor.low()