from machine import Pin, SPI
import os, uos, sys
sys.path.append('./lib/')
from sdcard import SDCard

spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0, firstbit=SPI.MSB, sck=Pin(2), mosi=Pin(3), miso=Pin(4))   # 100 KHz
sd = SDCard(spi, Pin(5))

vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

with open("/sd/test01.txt", "a") as file:
    file.write("Hello, SD World!\r\n")
    file.write("This is a test\r\n")

# Open the file we just created and read from it
with open("/sd/test01.txt", "r") as file:
    data = file.read()
    print(data)

uos.umount("/sd")