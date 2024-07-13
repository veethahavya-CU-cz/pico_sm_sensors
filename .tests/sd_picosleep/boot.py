with open ('sys.log', 'w') as f:
    f.write("********************* IN BOOT.PY *********************\n")

import os
import time
from machine import Pin, SoftI2C, SPI

from sdcard import SDCard
from ds1307 import DS1307

from picosleep import seconds as sleep
from time import sleep as pause

with open ('sys.log', 'a') as f:
    f.write("Imported modules\n")

led = Pin(25, Pin.OUT)
led.value(1)

with open ('sys.log', 'a') as f:
    f.write("Setting up RTC\n")

try:
    rtc_i2c = SoftI2C(scl=Pin(7), sda=Pin(6), freq=1_00_000)
    rtc_i2c.scan()

    clock = DS1307(rtc_i2c, 0x68)
    with open ('sys.log', 'a') as f:
        f.write("RTC time: {}\n".format(clock.datetime))
        f.write("Local time: {}\n".format(time.localtime()))
except Exception as e:
    with open ('sys.log', 'a') as f:
        f.write("Error: {}\n".format(e))


with open ('sys.log', 'a') as f:
    f.write("Setting up SD card\n")
try:
    sd_spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0, firstbit=SPI.MSB, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
    sd = SDCard(sd_spi, Pin(5))
    vfs = os.VfsFat(sd)
    os.mount(vfs, '/sd')
    with open ('sys.log', 'a') as f:
        f.write("SD card mounted\n")
except Exception as e:
    with open ('sys.log', 'a') as f:
        f.write("Error: {}\n".format(e))
# os.umount('/sd')

led.value(0)
with open ('sys.log', 'a') as f:
    f.write("Going to sleep...\n")
    f.write("********************* END BOOT.PY *********************\n")
# sleep(5)