# type: ignore
import sys, os
import time

sys.path.append('/lib')

import logging as log
from wrapper import rtc_setup, sd_mount
from helper import dir_exists, file_exists, get_config, strf_time

if file_exists('/config.json'):
    config = get_config()

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
    log.info("\n...\n\n\n\n...\n.......STARTING BOOT SEQUENCE.......\n...\n")

    last_recorded_time = time.localtime()
    log.critical(f"Last recorded time: {strf_time(last_recorded_time, 'time.localtime')}")


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
    machine.RTC().datetime(clock.datetimeRTC)
    log.info(f"Machine time updated. Machine time: {machine.RTC().datetime()}")
    
    with open('/sd/data/outages.rec', 'a') as f:
        f.write(f"OFFLINE: {strf_time(last_recorded_time)}\nONLINE: {strf_time(time.localtime())}\n\n")


    ### Create necessary output directories
    for key, value in config['path']['out'].items():
        if not dir_exists(value):
            log.critical(f"Output directory '{value}' not found. Creating directory.")
            os.mkdir(value)
    log.info("Output directories checked.")

else:
    with open('/ERR', 'w') as f:
        f.write("Config file not found!")


# TODO: sleep until next scheduled time