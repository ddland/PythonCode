import buildhat
import time

dist_sensor = buildhat.DistanceSensor('B')
motor = buildhat.Motor('A')
dist_sensor.eyes(0,0,50,50) # (Lup, Rup, Ldown, Rdown)

while True:
    dist = dist_sensor.get()[0]
    if dist > 0:
        if dist < 50:
            motor.run_for_degrees(30)
        elif dist < 80:
            print( motor.get_position())
    time.sleep(1)
