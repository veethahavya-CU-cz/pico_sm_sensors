import sys
from machine import SoftI2C, Pin
sys.path.append('./lib/')
from rtc import DS1307

i2c0 = SoftI2C(scl=Pin(7), sda=Pin(6), freq=1_00_000)
i2c0.scan()
clock = DS1307(i2c0, 0x68)

# get
clock.datetime

# set time (year, month, day, hours. minutes, seconds, weekday: integer: 0-6 )
clock.datetime = (2020, 12, 31, 4, 23, 59, 0, None)

"""
You can also access the current time with the :attr:`datetimeRTC` property.
        This returns the time in a format suitable for directly setting the internal RTC clock
        of the Raspberry Pi Pico (once the RTC module is imported).
"""