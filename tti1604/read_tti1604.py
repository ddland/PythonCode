import serial
import time
from tti1604 import TTI1604

if __name__ == "__main__":
    """ Example code for connecting and interacting with DMM on /dev/ttyUSB0."""
    
    import time
    tti = TTI1604('/dev/ttyUSB0')
    tti.send_command(b'e') # mA
    tti.send_command('l') # AC
    tti.send_command('u', debug=True)
    tti.send_command('g')

    run = True
    try:
        while run:
            print(tti.read())
            time.sleep(1)   
    except KeyboardInterrupt:
        run = False
