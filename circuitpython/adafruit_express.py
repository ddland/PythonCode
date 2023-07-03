# adapted from adafruit

import asyncio
import board
import neopixel
import time
from adafruit_circuitplayground import cp
import adafruit_fancyled.adafruit_fancyled as fancy

pixel_pin = board.A3
num_pixels = 7
order = neopixel.GRBW

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=order)

class Controls:
    """
    provides color palattes which can be used by button-presses

    allows to choose a palette and sets various controls to describe the state.
    """
    palette_evening = [fancy.CHSV(170, 125,255),  # blue
            fancy.CHSV(213,255,255),    #pink
            fancy.CHSV(255,255,255),    # red
            fancy.CHSV(255,255,0),      # dark-red, off
            fancy.CHSV(0,0,0),
    ]
    palette_rainbow = [fancy.CHSV(1,255,255),
                       fancy.CHSV(125,255,255),
                       fancy.CHSV(240,255,255),
                       ]

    def __init__(self):
        self.running = False
        self.on = False
        self.turn_off = True
        self.N = 60*60
        self.delay = 1.0 # 1 second for 1 hour
        self.set_palette()


    def set_palette(self, palette = 'evening'):
        if palette == 'rainbow':
            self.palette = self.palette_rainbow
        else:
            self.palette = self.palette_evening
        self.NP = len(self.palette)


async def rainbow_cycle(controls):
    """
    cycle trough the defined color palatte in controls.
    """
    while True:
        if controls.running and controls.on: # should do something
            steps = 2/(3*controls.N) #*(2/controls.NP)
            for j in range(controls.N):
                offset = steps *j
                if not controls.on:
                    break;
                color1 = fancy.palette_lookup(controls.palette,offset)
                color = fancy.gamma_adjust(color1)
                print(steps, j, controls.NP, controls.N, offset, color1)
                rgbw = [int(color.red*255), int(color.green*255), int(color.blue*255), 0]
                pixels.fill(rgbw)
                pixels.show()
                await asyncio.sleep(controls.delay)
            controls.on = False
            controls.turn_off = True
        controls.on = False
        if controls.turn_off:
            pixels.fill((0,0,0,0))
            pixels.show()
        await asyncio.sleep(0.01)

async def monitor_buttons(cp, controls):
    """Monitor buttons that reverse direction and change animation speed.
    Assume buttons are active low.
    """
    lastclick = time.monotonic()
    debounce = 0.1
    double = 2.0
    prevA = False
    prevB = False
    palette = 'evening'

    while True:
        currentclick = time.monotonic()
        dt_click = currentclick - lastclick
        if cp.button_a:
            if dt_click > debounce:
                controls.running = True
                controls.on = True
                lastclick = currentclick
        if cp.button_b:
            if dt_click > debounce:
                if palette == 'evening':
                    palette = 'rainbow'
                    controls.turn_off = False
                else:
                    palette = 'evening'
                    controls.turn_off = True
                controls.set_palette(palette)
                controls.on = False
                controls.running = False
                lastclick = currentclick
        await asyncio.sleep(0.01)


async def main():
    controls = Controls()

    buttons_task = asyncio.create_task(monitor_buttons(cp, controls))
    animation_task = asyncio.create_task(rainbow_cycle(controls))

    # This will run forever, because no tasks ever finish.
    await asyncio.gather(buttons_task, animation_task)


asyncio.run(main())