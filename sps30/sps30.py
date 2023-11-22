import machine
import time
import struct

# class for the Sensirion SPS30
# Connector:
# ---------------
# |       12345 |
# | *  *   *  * |
# ---------------
# Pin layout:
# 1: VDD (5V)
# 2: SDA
# 3: SCL
# 4: GRND (for I2C)
# 5: GND

class SPS30:
    address = 0x69
    start_measurement = [0x00, 0x10, 0x03, 0x00] # float numbers as return values
    data_header = ['mass pm 1.0', 'mass pm 2.5', 'mass pm 4.0', 'mass pm 10',
            'number pm 0.5', 'number pm 1.0', 'number pm 2.5', 'number pm 4.0',
            'number pm 10', 'typical size']
    
    def __init__(self, i2c, print_output=False):
        self.i2c = i2c
        self.output = print_output
        self.found = self.__findi2c()
    
    def write_read(self, cmd, nbytes=60):
        if len(cmd) == 2:
            cmd.append(self.calc_crc8(cmd))
        self.i2c.writeto(self.address, cmd)
        return self.i2c.readfrom(self.address, nbytes)
    
    def start_measurement(self):
        cmd = bytearray([0x00, 0x10, 0x03, 0x00, self.calc_crc8([0x03, 0x00])])
        self.i2c.writeto(self.address,cmd)
            
    def print_data(self):
        self.read_data()
        for ii, val in enumerate(self.last_measurement):
            print(self.data_header[ii], val)
    
    def read_data(self):
        cmd = bytearray([0x03, 0x00])
        data = self.write_read(cmd)
        cleandata = self.crc_array(data)
        self.last_measurement = []
        for ii in range(len(cleandata)//2):
            self.last_measurement.append(self.calcFloat(cleandata[2*ii] + cleandata[2*ii+1]))
        
        
    def __findi2c(self):
        if self.address in self.i2c.scan():
            if self.output:
                print('device found')
            return True
        else:
            return False
        
    def calc_crc8(self, byte_array):
        """
        Given an array of bytes calculate the CRC8 checksum.

        Args:
            byte_array (bytearray): The bytes needed to calculate the checksum
        
        Returns:
            crc (int): The calculated CRC8 checksum for the provided bytes
        """
        crc = 0xFF
        crc_poly = 0x131
        for byte in byte_array:
            crc ^= byte
            for bit in range(8):
                if crc & 0x80 != 0:
                    crc = (crc << 1) ^ crc_poly
                else:
                    crc = crc << 1
        return crc


    def check_crc8(self, byte_array, crc):
        if self.calc_crc8(byte_array) == crc:
            return True
        else:
            return False
    
    def crc_array(self, bt):
        nbytes = len(bt) // 3
        cleanarray = []
        if len(bt) % 3 != 0:
            print('error!')
        else:
            for ii in range(nbytes):
                start = ii*3
                stop  = ii*3+2
                if self.check_crc8(bt[start:stop], bt[stop]):
                    cleanarray.append(bt[start:stop])
        return cleanarray
    
    def calcFloat(self, byte_array):
        #Shamelessly stolen from the UnravelTec driver
        #TODO: Investigate using the struct library for other byte-bashing
        struct_float = struct.pack('>BBBB', byte_array[0], byte_array[1], byte_array[2], byte_array[3])
        return struct.unpack('>f', struct_float)[0]
            
if __name__ == "__main__":
    sda = machine.Pin(0)
    scl = machine.Pin(1)
    i2c = machine.I2C(0, sda=sda, scl=scl, freq=100000)
    sps30 = SPS30(i2c, print_output=True)
    time.sleep(5)
    sps30.start_measurement()
    run = True
    errors = 0
    while run:
        try:
            sps30.read_data()
            print(sps30.last_measurement)
            time.sleep(5)
            errors = 0
        except OSError as err: # sensor might give some EIO errors at startup
            errors += 1
            print(err, errors)
        except KeyboardInterrupt:
            run = False
        
    
