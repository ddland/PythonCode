# Hardware 

## motors

### 28BYJ-48
The [28BYJ-48](28byj48-step-motor-datasheet.pdf) is a cheap steppermotor. Together with the ULN2003 driverboard it is easy to setup.
For the wiring 4 GPIO pins from te RaspberryPi Pico are necessary. For testing purpose it is possible to use the VSYS from the RaspberryPi Pico. If using the motor (or multiple motors) at full power the powersupply should be an external one. 
![Wiring of the RaspberryPi Pico and the steppermotor](28BYJ.png)

The run the motor for 100 steps (there are about 2038 full steps in a revolution) with half steps: 
```python
import motor_step_28BYJ as motor
step = motor.Stepper28BYJ([0, 1, 2, 3], steps='half')
step.run(100)
```
or change the steps to full and the direction to counter-clockwise without creating a new motor object:
```python
step.set_steps(steps='full', direction='ccw')
step.run(2038//2)
```
Make sure both the [motor_step_28BYJ.py](motor_step_28BYJ.py) and [tools.py](tools.py) file are in the root of the RaspberryPi Pico.
