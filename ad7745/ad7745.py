import time
import machine

class AD7745:
    """
    Connect the AD7745 on the i2c bus.
    
    Allows all settings being written to the AD7746 and read.
    """
    address = 0x48 # 72 (7bit value)
    
    def __init__(self, i2c):
        self.i2c = i2c

    def read3(self, offset):
        """ read 3 bytes at offset offset from the AD7746

        arguments:
            offset: offset (from zero) for the register. Can be 1 or 4 for
                    capacity or voltage values
        return:
            capacity or voltage as 24 bit value
        """
        read = False
        value = None
        while not read:
            try:
                data = self.i2c.readfrom_mem(self.address, offset,3) # all registers
                value = (data[0] << 16 | data[1] << 8 | data[2]) #/ 2048 - 4096
                read = True
            except Exception as e:
                print(e)
        return value

    def register_to_hex(self,bits):
        # bits is a string with 0s and 1s.
        # left: bit 7, right: bit 0
        # like p14 of the datasheet
        return bytes([int(bits,2)])

    def write_register(self,reg,val):
        val = self.register_to_hex(val)
        self.i2c.writeto_mem(self.address, reg, val)

    def read_internaltemp(self):
        """ read VT Data register (voltage, temperature)

        return:
            temperature from internal sensor, converted to Celcius.
        """
        return (self.read3(4)/2048) - 4096
    
    def read_cap(self):
        # todo test values
        zero = 0x800000
        return 4.096*(self.read3(1) - zero)/zero

    def read_registers(self):
        settings = [0x07,0x08,0x09,0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12]
        for ii in settings:
            val = self.i2c.readfrom_mem(self.address, ii, 1)
            print(ii, '0x%02x' %(ord(val)))

    def read_offset(self, address):
        # 7 bit value stored in 8 bit address
        # 8th :1 cap enabled, 0: cap disabled
        offset = self.i2c.readfrom_mem(self.address, address, 1)[0] - 128
        if offset > 0:
            offset = offset * 0.164
        else:
            offset = 0
        return offset 
        
    def read_offsetA(self):
        return self.read_offset(0x0b)
    
    def read_offsetB(self):
        return self.read_offset(0x0c)

    def setup(self):
        self.write_register(0x07, '10000000') # enable CIN1
        self.write_register(0x08, '10000001') # enable volt as temperature
        self.write_register(0x09, '00001011') # enable EXC-A
        self.write_register(0x0a, '00100001') # continious conversion
        self.write_register(0x0b, '10000011') # DAC-A offset #127 steps
        self.write_register(0x0c, '01110100') # DAC-B offset (off)

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        try:
            while self.running:
                print('temp: ', self.read_internaltemp())
                print('cap:  ', self.read_cap())
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            
    def reset(self):
        # rest all registers to default
        self.i2c.writeto_mem(self.address, 0xbf, b'0x00')
        
if __name__ == "__main__":
    sda = machine.Pin(0)
    scl = machine.Pin(1)
    i2c = machine.I2C(0, sda=sda, scl=scl, freq=40000)
    print(i2c.scan())
    ad = AD7745(i2c)
    ad.setup()
    print(ad.read_internaltemp(), ad.read_cap(), ad.read_offsetA(), ad.read_offsetB())