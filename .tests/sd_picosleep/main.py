with open ('sys.log', 'a') as f:
    f.write("********************* IN MAIN.PY *********************\n")

import os
import time
from machine import Pin, SPI

from sdcard import SDCard

from picosleep import seconds as sleep
from time import sleep as pause

with open ('sys.log', 'a') as f:
    f.write("Imported modules\n")

led = Pin(25, Pin.OUT)

n = 0

while True:
    try:
        led.value(1)
        with open ('/sd/test', 'a') as f:
            f.write(f"[{n}]\n")
        with open ('sys.log', 'a') as f:
            f.write(f"SD card was mounted [{n}].\n")
    except Exception as e:
        sd_spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0, firstbit=SPI.MSB, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
        sd = SDCard(sd_spi, Pin(5))
        vfs = os.VfsFat(sd)
        os.mount(vfs, '/sd')
        with open ('sys.log', 'a') as f:
            f.write("SD card was not mounted. Mounting it again now.\n")
        
        for i in range(7):
            led.value(not led.value())
            pause(0.1)

    led.value(0)
    n += 1
    
    with open ('sys.log', 'a') as f:
        f.write("Going to sleep...\n\n")
    # sleep(3)
    pause(3)