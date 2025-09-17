from tti1604 import TTI1604
import time

if __name__ == "__main__":
    """ Example code for connecting and interacting with DMM on /dev/ttyUSB0."""
    
    tti = TTI1604('/dev/ttyUSB0') # change to COM4, COM5 or higher number on Windows
                                  # use MODE in the windows-terminal to find the correct
                                  # port.

    # or use the serial package to find the serial-ports (in a python-enabled terminal):
    # python -m serial.tools.list_ports
    # with -v added you will get even more information!
    
    # set TTI in mA mode with a binary string
    tti.send_command(b'e') 
    # set TTI in AC mode
    tti.send_command('l') 
    # set TTI in remote mode with extra debug information
    tti.send_command('u', debug=True)
    
    # enable if you want to turn-on the device (operate button).
    # when the device is off it will be turned on, but when it is on you will turn it 
    # off.
    # tti.send_command('g') 

    run = True
    try:
        while run:
            # long format including all information requiered for measurement 
            # uncertainty calculations
            val, acdc, range_info, range_type =  tti.read(full_output=True)
            print(val, range_type, acdc, range_info)
            
            # or using the tti-dictionaries to translate the numbers to something 
            # understandable, but hard to parse.
            print(val, tti.range_type_info[range_type], tti.acdc[acdc],
                  '(', tti.range_info[range_info], ')')

            # short format with just the value on the display
            val = tti.read()
            print(val)

            # wait a second before the next read-out.
            time.sleep(1)   
    except KeyboardInterrupt:
        run = False
    finally:
        # cleanup serial port
        tti.stop() 
