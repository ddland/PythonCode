import serial
import time

""" Read a TTI1604 DDM with Python.

Connect the device and set the serial port. After that use the commands:
 send_command(ser, command, debug=False)
   send a binary string (b'a' for example) to the device. Commands are
   the key-presses as if pressed on the device.
 char = read_data(ser)
   reads the data from the serial bus and stores the (10 characters) in char.
 parse_number_unit(char)
   parse the readout and returns the number from the display. If resistance is
   measured the kOhm or Ohm settings are taking into account.
 parse_data(char)
   parse all the data in the 10-char string from the device. 
   All settings are retreived.

20231102 
 initial release of the script. Working, but not documented / optimised yet.
"""

#####
# Keys
# Key Up = 'a'
# Key Down = 'b'
# Key Auto = 'c'
# Key A = 'd'
# Key mA = 'e'
# Key V = 'f'
# Key Operate = 'g'
# Key W = 'i'
# Key Hz = 'j'
# Key Shift = 'k'
# Key AC = 'l'
# Key DC = 'm'
# Key mV = 'n'
# Set remote mode = 'u'
# Set local mode = 'v'

def send_command(ser, command,debug=False):
    # cleanup state
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    # send command
    ser.write(command)
    time.sleep(0.3) # max timeout
    ret = ser.read(10)
    retval = False
    if len(ret) == 1:
        ret = chr(ret[0])
    print(ret, command.decode())
    if ret == command.decode():
        retval = True
    if debug:
        if retval:
            print('ok')
        else:
            print('not ok: ', command, ' ', ret)
    return retval 

def read_data(ser):
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser.read(10)
    
def parse_number(char):
    keys = {252: '0', 253: '0.',
            96: '1', 97: '1.',
            218: '2', 219: '2.',
            242: '3', 243: '3.',
            102: '4', 103: '4.',
            182: '5', 183: '5.',
            190: '6', 191: '6.',
            224: '7', 225: '7.',
            254: '8', 256: '8.',
            230: '9', 231: '9.',
            238: 'A', 156: 'C',
            122: 'D', 158: 'E',
            142: 'F', 140: 'R',
            30: 'T', 124: 'U',
            28: 'L', 0: '', 2: '',
            }         
    val = ''
    if char[3] & 1 << 0 != 0: 
        val = '-'
    for ii in range(4,9):
        if char[ii] in keys.keys():
            val += keys[char[ii]]
    try:
        val = float(val)
    except ValueError:
        pass
    return val

def parse_number_unit(char):
    val = parse_number(char)
    dmm_range  = (char[1] & (( 1 << 7) -1))  >> 4
    dmm_type = char[1] & (( 1 << 3) -1) # last 3 bits
    if isinstance(val, float) and  (dmm_type == 5) and (dmm_range != 0):
        val = val*1000
    return val
    
def parse_data(char):
    range_type_info = {1: 'mV', 2: 'V', 3: 'mA', 4: 'A', 5: 'Ohm', 6: 'Continuity', 7:'Diode Test'}
    range_info = {0: '400 Ohm',
                  1: '4 kOhm / 4 Vac / 4 Vdc / 4 mAdc / 1 mAac',
                  2: '40 kOhm / 40 Vac / 40 Vdc / 10 Adc / 10 Aac',
                  3: '400 kOhm / 400 Vac / 400 Vdc / 400 mAdc / 400 mAac / 400 mVdc / 400 mVac',
                  4: '4 MOhm / 750 Vac / 1000 Vdc',
                  5: '40 MOhm',
                  }
    acdc = {0: 'DC', 1: 'AC'}
    if char[0] != 13: # else no data
        return False
    dmm_type = char[1] & (( 1 << 3) -1) # last 3 bits
    dmm_acdc = (char[1] & (( 1 << 4) -1)) >> 3  # 1 AC, 0 DC
    dmm_range  = (char[1] & (( 1 << 7) -1))  >> 4
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
    val = parse_number_unit(char)
    print('_______________________________________________________________________')    
    print(range_type_info[dmm_type], acdc[dmm_acdc], range_info[dmm_range])
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
    

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB1', baudrate=9600, dsrdtr=0, timeout=1)
    ser.rts = 0
    ser.dtr = 1

    send_command(ser, b'e') # mA
    send_command(ser, b'l') # AC

    retval = False
    while not retval:
        retval = send_command(ser, b'u', debug=True)

    data = ser.read(10)
    

    
    
