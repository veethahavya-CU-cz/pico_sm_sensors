# type: ignore
import sys
from machine import RTC, Pin

from time import localtime, time
# from picosleep import seconds as sleep
from machine import deepsleep as sleep
from time import sleep as pause


sys.path.append('/lib/')

import logging as log
from wrapper import rtc_setup, sd_mount, read_sm, read_internal_temp, read_battery
from helper import get_config, dir_exists, file_exists, prep_next_ts


led = Pin('LED', Pin.OUT)
switch = Pin(15, Pin.IN)

### Read config file
config = get_config()


### Setup RTC if not defined
if 'clock' not in globals():
    log.info("Setting up RTC")
    clock = rtc_setup()
    log.info("RTC setup complete")

    log.info("Updating machine time")
    RTC().datetime(clock.datetimeRTC)
    log.info(f"Machine time updated. Machine time: {RTC().datetime()}")

### Mount SD Card if not mounted
if not dir_exists(config['path']['sd_root']):
    log.info("Mounting SD Card")
    check = sd_mount()
    if not check:
        log.error("SD Card could not be mounted")
        raise Exception("SD Card could not be mounted")
    log.info("SD Card mounted")


while True:
    while switch.value() == 1:
        for _ in range(7):
            led.on()
            pause(0.1)
            led.off()
            pause(0.1)
        ### Read recording parameters
        if file_exists(config['path']['out']['cache'] + '/recs'):
            with open(config['path']['out']['cache'] + '/recs', 'r') as f:
                recs = f.read().splitlines()
                log.info(f"Read recording parameters: {recs}")
        else:
            log.critical("Recording parameters not found in cache")

        if file_exists(config['path']['out']['cache'] + '/rec_time'):
            with open(config['path']['out']['cache'] + '/rec_time', 'r') as f:
                next_record_time = int(f.readline().strip())
                next_record_timestamp = f.readline().strip()
                log.info(f"Read next record time: {next_record_time} ({next_record_timestamp})")
        else:
            log.critical("Next record time not found in cache")

        # if next_record_time - time() > config['time']['interval']['SM']['sampling'] * config['samples']['per_red']['SM'] + 3:
        #     log.info(f"Pausing for {next_record_time - time()} seconds")
        # pause(next_record_time - time())

        if 'SM' in recs:
            log.info("Reading soil moisture")
            readings = read_sm(config['nsensors']['SM'])
            log.info("Writing soil moisture readings to records")
            with open(config['fpath']['sm'], 'a') as f:
                if config['nsensors']['SM'] == 1:
                    f.write(f"{next_record_timestamp}, {readings['SM1']['mean']}\n")
                elif config['nsensors']['SM'] == 2:
                    f.write(f"{next_record_timestamp}, {readings['SM1']['mean']}, {readings['SM2']['mean']}\n")
                elif config['nsensors']['SM'] == 3:
                    f.write(f"{next_record_timestamp}, {readings['SM1']['mean']}, {readings['SM2']['mean']}, {readings['SM3']['mean']}\n")
            log.info("Soil moisture readings written to records")

        if 'DHT11' in recs:
            log.info("Reading temperature and humidity")
            pass
        # TODO: Implement DHT11 reading

        if 'ITEMP' in recs:
            log.info("Reading internal temperature")
            temperature = read_internal_temp()
            log.info("Writing internal temperature to data")
            with open(config['fpath']['itemp'], 'a') as f:
                f.write(f"{next_record_timestamp}, {temperature}\n")

        if 'BATT' in recs:
            log.info("Reading battery voltage")
            voltage, percentage = read_battery()
            log.info("Writing battery voltage to data")
            with open(config['fpath']['battery'], 'a') as f:
                f.write(f"{next_record_timestamp}, {voltage}, {percentage}\n")


        ### Calculate next record time
        next_record_time, next_record_timestamp = prep_next_ts()
        led.off()
        if next_record_time - time() > config['time']['wake_haste']:
            log.info(f"Sleeping until next record time: {strf_time(next_record_time)}")
            sleep(next_record_time - time() - config['time']['wake_haste'])
        else:
            log.info("Next record time is too close. Skipping sleep.")
            pause(next_record_time - time())
    
    while switch.value() == 0:
        log.info("Recording turned off. Pausing for 60 seconds")
        pause(60)
        log.info("Resuming switch check")