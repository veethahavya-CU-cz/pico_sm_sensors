# type: ignore
from sys import path
from machine import RTC, Pin
from utime import time
from time import sleep as pause
from machine import lightsleep as sleep

path.append('/lib/')
import logging as log
from wrapper import rtc_setup, sd_mount
from helper import dir_exists, file_exists, get_config, strf_time, prep_next_ts



led = Pin('LED', Pin.OUT)
led.on()
log.info("\n...\n\n\n\n...\n.......STARTING BOOT SEQUENCE.......\n...\n")

# Read config file
if file_exists('/config.json'):
    CONFIG = get_config()
    
    # Setup SD Card
    if not dir_exists(CONFIG['path']['sd_root']):
        log.info("Mounting SD Card")
        if not sd_mount():
            log.error("SD Card could not be mounted")
            raise Exception("SD Card could not be mounted")
        log.info("SD Card mounted")

    # Setup logging
    if CONFIG['IO']['log']['UART']:
        uart_out = [CONFIG['Pin']['UART']['BUS'], CONFIG['time']['interval']['UART_BAUD'], CONFIG['Pin']['UART']['TX'], CONFIG['Pin']['UART']['RX']]
    else:
        uart_out = None
    log.init(file=CONFIG['IO']['log']['file'], lvl=CONFIG['IO']['log']['level'], rewrite=True, uart_out=uart_out)

    # Check necessary source and library files
    log.info("Checking necessary files")
    for file in CONFIG['files']['src'] + CONFIG['files']['lib']:
        path = CONFIG['path']['src'] + '/' + file if file in CONFIG['files']['src'] else CONFIG['path']['lib'] + '/' + file
        if not file_exists(path):
            log.critical(f"File '{file}' not found in '{path}'")
            raise Exception(f"File '{file}' not found in '{path}'")
    log.info("All necessary files found")

    # Setup RTC
    log.info("Setting up RTC")
    clock = rtc_setup()
    log.info("RTC setup complete")
    if clock.disable_oscillator:
        log.critical("RTC oscillator was disabled! Enabling RTC oscillator.")
        clock.disable_oscillator = False
        log.info("RTC oscillator enabled.")
    log.info("Updating machine time")
    internal_clock = RTC()
    internal_clock.datetime(clock.datetimeRTC)
    log.info(f"Machine time updated: {RTC().datetime()}")


    # Create necessary output directories
    for value in CONFIG['path']['out'].values():
        if not dir_exists(value):
            log.critical(f"Output directory '{value}' not found. Creating.")
            os.mkdir(value)
    log.info("Output directories checked.")

else:
    with open('/ERR', 'w') as f:
        f.write("Config file not found!")
    log.critical("Config file not found!")
    raise Exception("Config file not found!")

# Calculate next record time
next_record_time, next_record_timestamp = prep_next_ts()
led.off()

# Sleep or pause until the next record time
time_to_next_record = next_record_time - time()
if time_to_next_record > CONFIG['time']['wake_haste']:
    log.info(f"Sleeping until next record time: {strf_time(next_record_time, 'time.time')}, for {time_to_next_record} seconds.")
    sleep((time_to_next_record - CONFIG['time']['wake_haste']) * 1000)
    log.info("Woke up from sleep (@boot). Starting main loop.")
else:
    log.info("Next record time is too close. Skipping sleep.")
    pause(time_to_next_record)
    log.info("Starting main loop.")