import serial
import time

""" Read a TTI1604 DDM with Python.

Connect the device and set the serial port. After that use the commands:

    send_command(str)
        Send the key-presses to the DMM in order to configure the device.
    val = read()
        Read the display value on the DMM into the variable val.
    val, acdc, range_info, range_type =  tti.read(full_output=True)
        Read the display value and all the settings of the reading.
        The settings are the dictionary keys for the TTI class.

The DMM has multiple keys which can activate the settings. Changing the settings
is done as if you press the keys on the front of the device.
Every key has a character translation. Sending the character to the device is
the same as pressing the key.

For example, setting Null on the screen involes the shift-key and the DC key.
Two send commands are requiered with the characters 'k' (shift) and 'm' (DC).
The characters are given in the table below:
---------------------
keys		character
Up				'a'
Down			'b'
Auto 			'c'
A 				'd'
mA 				'e'
V 				'f'
Operate 		'g'
Ohm 			'i'
Hz 				'j'
Shift 			'k'
AC 				'l'
DC 				'm'
mV 				'n'
set remote mode	'u'
set local mode 	'v'
----------------------
Only in remote mode the device will send data back to the serial port after a
measurement.

20231102 
 initial release of the script. Working, but not documented / optimised yet.
20250917
 added tti.stop() to hopefully close the serial port
 extended tt.read() with full_output=True which also returns the settings of the value.
"""

class TTI1604:
    keys = {252: '0', 253: '0.',
            96: '1', 97: '1.',
            218: '2', 219: '2.',
            242: '3', 243: '3.',
            102: '4', 103: '4.',
            182: '5', 183: '5.',
            190: '6', 191: '6.',
            224: '7', 225: '7.',
            254: '8', 255: '8.',
            230: '9', 231: '9.',
            238: 'A', 156: 'C',
            122: 'D', 158: 'E',
            142: 'F', 140: 'R',
            30: 'T', 124: 'U',
            28: 'L', 0: '', 2: '',
            }
    range_type_info = {1: 'mV', 2: 'V', 3: 'mA', 4: 'A', 5: 'Ohm', 6: 'Continuity', 7:'Diode Test'}
    range_info = {0: '400 Ohm',
                  1: '4 kOhm / 4 Vac / 4 Vdc / 4 mAdc / 1 mAac',
                  2: '40 kOhm / 40 Vac / 40 Vdc / 10 Adc / 10 Aac',
                  3: '400 kOhm / 400 Vac / 400 Vdc / 400 mAdc / 400 mAac / 400 mVdc / 400 mVac',
                  4: '4 MOhm / 750 Vac / 1000 Vdc',
                  5: '40 MOhm',
                  }
    acdc = {0: 'DC', 1: 'AC'}
    
    def __init__(self, tty):
        """ Initialise the DMM
        argument:
            tty - TTY device string on which the DMM is connected. Exmple:
                '/dev/ttyUSB0'
        return:
            None
        """
        self.ser = serial.Serial(tty, baudrate=9600, dsrdtr=0, timeout=1)
        self.ser.rts = 0
        self.ser.dtr = 1
     
    def stop(self):
        self.ser.close()


    def read_raw_data(self):
        """ Read a string of 10 bytes from the serial bus
        arguments:
            None
        return:
            bytestring - collected data from the serial bus (bytestring)
        """
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        return self.ser.read(10)
    
    def read(self, full_output=False):
        """ Read a value from the DMM
        arguments:
            full_output [default False] - give full output if true (value, unit, AC/DC,
            range) where value is the measured numerical value, unit the physical unit
            of the measuremnt, AC/DC the setting for altenating or direct current
            measurements and the range the allowed input range for the current settings.
            If False only the value is returned.
        return:
            float - value on display. If resistance is measured the return value is
                    in Ohms.
            if full_output = True:
                    float, int, int, int: where float is the value on display and the
                    ints are the dictionary keys for the ACDC, range_info and 
                    range_type_info dictonaries defined within this class.
        """
        return self.parse_number_unit(self.read_raw_data(), full_output)
    
    def parse_number(self, char=None):
        """ Parse the 10 byte string from the DMM into a number
        arguments:
            char - bytestring or None
                converts the bytestring into a number or reads the data from
                the device and converts it into a number.
        return:
            float - value on display
        """
        if not char:
            char = self.read_raw_data()
        if len(char) == 0:
            print('no data measured. Is the device in remote mode (u) or on (g)?')
            return False
        val = ''
        if char[3] & 2 << 0 != 0: 
            val = '-'
        for ii in range(4,9):
            if char[ii] in self.keys.keys():
                val += self.keys[char[ii]]
        try:
            val = float(val)
        except ValueError:
            pass
        return val

    def parse_number_unit(self, char=None, full_output=False):
        """ Parse the 10 byte string from the DMM into a number
        arguments:
            char - bytestring or None
                converts the bytestring into a number or reads the data from
                the device and converts it into a number. Takes into account
                the kOhm or Ohm settings on the display.
        return:
            float - value on display
        """
        if not char:
            char = self.read_raw_data()
        if len(char) == 0:
            print('no data measured. Is the device in remote mode?')
            return False
        val = self.parse_number(char)
        dmm_acdc = (char[1] & (( 1 << 4) -1)) >> 3  # 1 AC, 0 DC
        dmm_range  = (char[1] & (( 1 << 7) -1))  >> 4
        dmm_type = char[1] & (( 1 << 3) -1) # last 3 bits
        # multiple Ohms by 1000 (if kOhm ligth is on)
        if isinstance(val, float) and  (dmm_type == 5) and (dmm_range != 0):
            val = val*1000
        if full_output:
            return val, dmm_acdc, dmm_range, dmm_type
        else:
            return val

    def show_settings(self, char=None):
        """ Show all settings of the measurement
        arguments:
            char - bytestring or None
                If char is a bytestring displays all settings from the bytesting,
                otherwise reads the data first and displays all settings.
        return:
            None
        """        
        if not char:
            char = self.read_raw_data()
        if len(char) == 0:
            print('no data measured. Is the device in remote mode?')
            return False
        if char[0] != 13: # else no data
            return False
        dmm_type = char[1] & (( 1 << 3) -1) # last 3 bits
        dmm_acdc = (char[1] & (( 1 << 4) -1)) >> 3  # 1 AC, 0 DC
        dmm_range  = (char[1] & (( 1 << 7) -1))  >> 4 # first 3 bits
        thold = char[2] & 1  != 0
        minmax = char[2] & 1 <<  2 != 0
        hertz = char[2] & 1 << 4 != 0
        null = char[2] & 1 <<  5 != 0
        auto = char[2] & 1 << 6 != 0
        minus = char[3] & 1 << 0 != 0 
        doublebeep = char[9] & 1 != 0
        autorange = char[9] & 1 << 2 != 0
        contbuzz = char[9] & 1 << 3  != 0
        dispmin = char[9] & 1 << 4 != 0
        dispmax = char[9] & 1 << 5 != 0
        disphold = char[9] & 1 << 6 != 0
        gate10sec = char[9] & 1 << 7 != 0
        val = self.parse_number_unit(char)
        print('_______________________________________________________________________')    
        print('measurement: ', self.range_type_info[dmm_type])
        print('AC or DC: ', self.acdc[dmm_acdc])
        print('measurement range: ', self.range_info[dmm_range])
        print('Thold: ', thold)
        print('MinMax: ', minmax)
        print('Hertz: ', hertz)
        print('NULL: ', null)
        print('Auto: ', auto)
        print('DoubleBeep: ', doublebeep)
        print('AutoRangeSet : ', autorange )
        print('Cont Buz : ', contbuzz )
        print('Disp Min : ', dispmin )
        print('Disp Max : ', dispmax )
        print('Disp Hold : ', disphold )
        print('Gate 10 sec : ', gate10sec)
        print('value: ', val)
        print('_______________________________________________________________________')      
        

    def send_command(self, command,debug=False):
        """ Send a command to the DMM
        arguments:
            command:
                bytestring or string - the single letter command for the DMM
            debug:
                True / False (default False) - display extra debug information
        return:
            True / False - true if command is well-received by the DMM, False
            otherwise.
        """
        # command needs to be byte-string
        if isinstance(command, str):
            command = bytes(command, 'ascii')
        # cleanup state
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        # send command
        self.ser.write(command)
        time.sleep(0.3) # max timeout
        ret = self.ser.read(10)
        retval = False
        if len(ret) == 1:
            ret = chr(ret[0])
        if ret == command.decode():
            retval = True
        if debug:
            if retval:
                print('ok')
            else:
                print('not ok: ', command, ' ', ret)
        return retval
    
    def print_keys(self):
        """ Print all display-keys of the DMM.
        Table with characters are used for sending commands to the DMM.
        arguments:
            None
        return:
            None
        """
        keys = """
---------------------
keys		character
Up		'a'
Down		'b'
Auto 		'c'
A 		'd'
mA 		'e'
V 		'f'
Operate 	'g'
Ohm 		'i'
Hz 		'j'
Shift 		'k'
AC 		'l'
DC 		'm'
mV 		'n'
set remote mode	'u'
set local mode 	'v'
----------------------
"""
        print(keys)

if __name__ == "__main__":
    """ Example code for connecting and interacting with DMM on /dev/ttyUSB0."""
    
    import time
    tti = TTI1604('/dev/ttyUSB0')
    tti.send_command(b'e') # mA
    tti.send_command('l') # AC
    tti.send_command('u', debug=True)
    tti.send_command('g')

    while True:
        print(tti.read())
        time.sleep(1)
    

    
    
