import ad7745
import time
import machine

if __name__ == "__main__":
    # First I2C port
    pico_id = 1
    sda1 = machine.Pin(0)
    scl1 = machine.Pin(1)
    i2c = machine.I2C(0, sda=sda1, scl=scl1, freq=40000)
    
    # raspberrypi pico (not W!)
    led = machine.Pin(25, machine.Pin.OUT)


    # Configure first AD7745 device
    ad = ad7745.AD7745(i2c)
    ad.reset()
    time.sleep(0.5)

    ad.write_register(0x07, '10000000') # enable CIN1
    ad.write_register(0x08, '10000001') # enable volt as temperature
    ad.write_register(0x09, '00001011') # enable EXC-A
    ad.write_register(0x0a, '00111001') # continious conversion
    ad.write_register(0x0b, '00000000') # DAC-A offset #127 steps
    ad.write_register(0x0c, '00000000') # DAC-B offset (off)
    time.sleep(1)
    measurement = ad.read_cap()

    run = True

    while True:
        if run:
            try:
                led.on()
                measurement = ad.read_cap()
                offset = ad.read_offsetA()
                int_temp = ad.read_internaltemp()  # read internal temperature
                print(pico_id, measurement, offset, int_temp, '\r\n')
                time.sleep(5)
                led.off()
                time.sleep(5)
            except KeyboardInterrupt:
                run = False





