# FIXME: Recording stops on month change. Need to debug time-caching, time-checking, and wake logic.

from usys import path as sys_path
from machine import RTC, Pin
from utime import time
from time import sleep as pause
from machine import lightsleep as sleep

from os import path

sys_path.insert(0, '/usr/lib')
import picostation_logging as log
from picostation_helper import get_config, prep_next_ts
from picostation_wrapper import rtc_setup, sd_mount, status_led


status_led('busy')
led = Pin('LED', Pin.OUT)
led.on()
log.info("\n...\n\n\n\n...\n.......STARTING BOOT SEQUENCE.......\n...\n")

# Read config file
if path.exists('/config.json'):
    CONFIG = get_config()

    # Setup SD Card
    if not path.exists(CONFIG['path']['sd_root']):
        log.info("Mounting SD Card")
        if not sd_mount():
            status_led('flash/error_sd')
            log.error("SD Card could not be mounted")
            raise Exception("SD Card could not be mounted")
        log.info("SD Card mounted")

    # Setup logging
    if CONFIG['IO']['log']['UART']:
        uart_out = [
            CONFIG['Pin']['UART']['BUS'],
            CONFIG['BAUD']['UART'],
            CONFIG['Pin']['UART']['TX'],
            CONFIG['Pin']['UART']['RX'],
        ]
    else:
        uart_out = None
    log.init(file=CONFIG['IO']['log']['file'], lvl=CONFIG['IO']['log']['level'], rewrite=False, uart_out=uart_out)

    # Setup RTC
    try:
        log.info("Setting up RTC")
        clock = rtc_setup()
        log.info("RTC setup complete")
        if clock.halt:
            log.critical("RTC clock was halted! Enabling RTC oscillator.")
            clock.halt = False
            log.debug("RTC oscillator enabled.")
        log.info("Updating machine time")
        internal_clock = RTC()
        internal_clock.datetime((clock.year, clock.month, clock.day, clock.weekday, clock.hour, clock.minute, clock.second, 0))
        log.info(f"Machine time updated: {RTC().datetime()}")
    except Exception as e:
        status_led('flash/error_rtc')
        log.critical(f"Failed to setup RTC: {e}")
        raise Exception("Failed to setup RTC")

else:
    with open('/ERR', 'w') as f:
        f.write("Config file not found!")
        status_led('error')
    log.critical("Config file not found!")
    raise Exception("Config file not found!")

# Calculate next record time
next_record_time, next_record_timestamp = prep_next_ts()
led.off()
status_led('off')
pause(CONFIG['time']['sleep_buffer_pause'])

# Sleep or pause until the next record time
time_to_next_record = next_record_time - time()
if time_to_next_record > CONFIG['time']['wake_haste']:
    log.info(f"Sleeping until next record time: {next_record_timestamp}, for {time_to_next_record} seconds.")
    pause(CONFIG['time']['sleep_buffer_pause'])
    sleep((time_to_next_record - CONFIG['time']['wake_haste']) * 1000)
    pause(CONFIG['time']['sleep_buffer_pause'])
    log.info("Woke up from sleep (@boot). Starting main loop.")
else:
    log.info("Next record time is too close. Skipping sleep.")
    pause(time_to_next_record)
    log.info("Starting main loop.")
