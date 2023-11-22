import serial
import time

""" Read serial data from SPS30 (micropython)

Example scripts which reads the data from the SPS30 particulate matter sensor
and logs the data, with a timestamp, to a file. 
Also prints all the data to the terminal.

Change the serial port and output.
"""

ser = serial.Serial('/dev/ttyACM0')
output = 'datafile.csv'

fh = open(output, 'a')
run = True

while run:
    try:
        data = ser.readline().decode().strip()[1:-1].split(',')
        data = [float(ii) for ii in data]
        data_str = ''
        for val in data:
            data_str += '%4.3f,' %val
        data_str = data_str[:-1] # remove extra ,
        data_str = str(time.time()) + ',' + data_str + '\n'
        fh.write(data_str)
        fh.flush()
        print(data_str[:-1])
    except KeyboardInterrupt:
        run = False
    except Exception as err: # garbage on serial bush, no need to print
        print(err)
fh.close()
