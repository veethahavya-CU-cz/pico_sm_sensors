# type: ignore
import sys
from machine import RTC, Pin

from time import localtime, time
# from picosleep import seconds as sleep
from machine import lightsleep as sleep
from time import sleep as pause


sys.path.append('/lib/')

import logging as log
from wrapper import rtc_setup, sd_mount
from helper import dir_exists, file_exists, get_config, strf_time, prep_next_ts


led = Pin('LED', Pin.OUT)
led.on()

log.info("\n...\n\n\n\n...\n.......STARTING BOOT SEQUENCE.......\n...\n")

### Read config file
if file_exists('/config.json'): 
    config = get_config()

    if not dir_exists(config['path']['sd_root']):
        ### Setup SD Card
        if not dir_exists(config['path']['sd_root']):
            log.info("Mounting SD Card")
            check = sd_mount()
            if not check:
                log.error("SD Card could not be mounted")
                raise Exception("SD Card could not be mounted")
            log.info("SD Card mounted")
    
    ### Setup logging
    log.init(config['fpath']['log'], config['IO']['log']['level'], rewrite=False)

    last_recorded_time = localtime() #FIXME: This should be the last recorded time from the SD card
    log.critical(f"Last recorded time: {strf_time(last_recorded_time, 'time_tuple')}")


    ### Check if necessary source and library files exist
    log.info("Checking if necessary source and library files exist")

    for file in config['files']['src']:
        if not file_exists(config['path']['src'] + '/' + file):
            log.critical(f"Source file '{file}' not found in '{config['path']['src']}'")
            raise Exception(f"Source file '{file}' not found in '{config['path']['src']}'")

    for file in config['files']['lib']:
        if not file_exists(config['path']['lib'] + '/' + file):
            log.critical(f"Library file '{file}' not found in '{config['path']['lib']}'")
            raise Exception(f"Library file '{file}' not found in '{config['path']['lib']}'")

    log.info("All necessary source and library files found")


    ### Setup RTC
    log.info("Setting up RTC")
    clock = rtc_setup()
    log.info("RTC setup complete")

    if clock.disable_oscillator:
        log.critical("RTC oscillator was disabled! Enabling RTC oscillator.")
        clock.disable_oscillator = False
        log.info("RTC oscillator enabled.")

    log.info("Updating machine time")
    RTC().datetime(clock.datetimeRTC)
    log.info(f"Machine time updated. Machine time: {RTC().datetime()}")
    
    with open('/sd/data/outages.rec', 'a') as f:
        f.write(f"OFFLINE: {strf_time(last_recorded_time)}\nONLINE: {strf_time(localtime())}\n\n")


    ### Create necessary output directories
    for key, value in config['path']['out'].items():
        if not dir_exists(value):
            log.critical(f"Output directory '{value}' not found. Creating directory.")
            os.mkdir(value)
    log.info("Output directories checked.")

else:
    with open('/ERR', 'w') as f:
        f.write("Config file not found!")
    log.critical("Config file not found!")
    raise Exception("Config file not found!")


### Calculate next record time
next_record_time, next_record_timestamp = prep_next_ts()
led.off()
if next_record_time - time() > config['time']['wake_haste']:
    log.info(f"Sleeping until next record time: {strf_time(next_record_time)}")
    sleep(next_record_time - time() - config['time']['wake_haste'])
else:
    log.info("Next record time is too close. Skipping sleep.")
    pause(next_record_time - time())