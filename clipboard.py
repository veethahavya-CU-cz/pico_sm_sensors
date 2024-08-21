from ds1307 import DS1307
from machine import I2C, Pin
rtc_i2c = I2C(id=1, sda=Pin(6), scl=Pin(7), freq=80_000)
rtc_i2c.scan()

clock = DS1307(i2c=rtc_i2c)


from machine import SPI, Pin
from sdcard import SDCard

spi = SPI(id=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))

sd = SDCard(spi, Pin(5))
uos.mount(sd, '/sd')