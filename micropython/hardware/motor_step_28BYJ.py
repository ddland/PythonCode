import machine
import time
import tools


class Stepper28BYJ:
    """Class for the Stepper motor 28BYJ-48.

    class attributes:
        _stepsH: list of lists for the values of the motor_pins. Only the
               half-step is given. Fullstep and waveform are inferred from
               halfstep.
        _iter: iterator object which is a circular iterator of the
               stepsize-lists.
    """
    _stepsH = [[0, 0, 0, 1],
               [0, 0, 1, 1],
               [0, 0, 1, 0],
               [0, 1, 1, 0],
               [0, 1, 0, 0],
               [1, 1, 0, 0],
               [1, 0, 0, 0],
               [1, 0, 0, 1]]

    _iter = None

    def __init__(self, pins: list, steps='half', direction='cw') -> None:
        """Initialize the motor-object.

        arguments:
            pins: machine pins (raspberrypi pico pin (0,1,2,3) works well
                  with motor pins (1,2,3,4).
            steps: either half (default), full or wave. Determines the
                  stepsize.
            direction: clockwise (cw, default) or counterclockwise).
        """
        self.motor = [machine.Pin(ii, machine.Pin.OUT) for ii in pins]
        self.npins = len(pins)
        self.set_steps(steps, direction)

    def set_steps(self, steps: str, direction: str):
        """ Configures the step-iterator.

        The iterator will always return the next value for smooth operation
        of the motor.

        arguments:
            steps: type of step (full, half, or wave)
            direction: clockwise or counterclockwise)
        """
        self.direction = direction
        self.steps = steps
        self.reset()
        if steps == 'full':
            if direction == 'cw':
                self._iter = iter(tools.Circular(self._stepsH[1::2]))
            else:
                self._iter = iter(tools.Circular(self._stepsH[1::2],
                                  reversed=True))
        elif steps == 'wave':
            if direction == 'cw':
                self._iter = iter(tools.Circular(self._stepsH[::2]))
            else:
                self._iter = iter(tools.Circular(self._stepsH[::2],
                                  reversed=True))
        else:
            if direction == 'cw':
                self._iter = iter(tools.Circular(self._stepsH))
            else:
                self._iter = iter(tools.Circular(self._stepsH, reversed=True))

    def reset(self) -> None:
        """ Set all outputs to zero (low). """
        [ii.value(0) for ii in self.motor]

    def step(self):
        """ Send the next step to the motor. """
        values = next(self._iter)
        for ii in range(self.npins):
            self.motor[ii].value(values[ii])

    def run(self, N=530*8, delay=0.002, off=True):
        """ Run the motor for a number of steps.

        arguments:
            N: number of steps, default 530*8. With halfsteps about 512*8 steps
               is a full-circle, for full-steps or waves this is 512*4.
            delay: delay before next step is send to the motor.
                If the delay is too small, the motor does not function.
                off: set all output ports to zero after the number of steps is
                 finished
        """
        if (self.steps == 'wave' or self.steps == 'full') and delay < 0.002:
            print("Delay too small. Motor might not respond correctly.")

        elif (self.steps == 'half' and delay < 0.001):
            print("Delay too small. Motor might not respond correctly.")

        for i in range(N):
            self.step()
            time.sleep(delay)

        if off:
            self.reset()


if __name__ == "__main__":
    step = Stepper28BYJ([0, 1, 2, 3], steps='full')
    step.run()
