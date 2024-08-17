from definitions import logfile, outfiles
import logging


open(logfile, 'w').close()
### log machine info [id, sensors, location, ...] ###


### set RTC time and sync machine time to it ###


for file in outfiles:
    open(file, 'w').close()