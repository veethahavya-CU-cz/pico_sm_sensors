import os
from utime import sleep

from definitions import led, outfiles

led.off()
for i in range(3 *2):
    led.toggle()
    sleep(0.5)


### get and set time from RTC ###

### schedule logging for the nearest upcoming scheduled time-anchor based on the logging interval and sleep ###


# Create files if they are deleted during outage(s) and log error
for file in outfiles:
    try:
        open(file, 'r').close()
    except OSError:
        # TODO: Log error
        open(file, 'w').close()