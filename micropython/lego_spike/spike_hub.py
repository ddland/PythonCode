import time

time.sleep(1) # need a delay else no connected hardware detected!

# example where a motor is connected to port A and a distance sensor to port C
# moves the motor 30 degrees forward if an object is detected within 10 cm.

# todo
# figure out how to read the current angle from the motor

# based on
# https://antonsmindstorms.com/2021/01/14/advanced-undocumented-python-in-spike-prime-and-mindstorms-hubs/

dist_sensor = hub.port.C.device
motor = hub.port.A.motor

while True:
    dist = dist_sensor.get()[0]
    if dist:
        if dist < 10:
            motor.run_for_degrees(30)
        elif dist < 20:
            print(motor.get())
    time.sleep(1)
    print('motor: ', motor.get())
    
