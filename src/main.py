# type: ignore
from usys import path
from utime import time
from utime import sleep as pause
from machine import RTC, Pin
from machine import lightsleep as sleep

path.append('/lib/')

import logging as log
from wrapper import rtc_setup, sd_mount, read_sm, read_internal_temp, read_battery
from helper import get_config, dir_exists, file_exists, prep_next_ts, strf_time

led = Pin('LED', Pin.OUT)
logger_switch = Pin(15, Pin.IN)

# Read config file
config = get_config()

# Setup RTC
if 'clock' not in globals():
    log.info("Setting up RTC")
    clock = rtc_setup()
    log.info("RTC setup complete")

    log.info("Updating machine time")
    RTC().datetime(clock.datetimeRTC)
    log.info(f"Machine time updated: {RTC().datetime()}")

# Mount SD Card
if not dir_exists(config['path']['sd_root']):
    log.info("Mounting SD Card")
    if not sd_mount():
        log.error("SD Card could not be mounted")
        raise Exception("SD Card could not be mounted")
    log.info("SD Card mounted")

while True:
    if logger_switch.value():
        for _ in range(7):
            led.on()
            pause(0.1)
            led.off()
            pause(0.1)

        # Read recording parameters
        recs_path = config['path']['out']['cache'] + '/recs'
        if file_exists(recs_path):
            with open(recs_path, 'r') as f:
                recs = f.read().splitlines()
                log.info(f"Read recording parameters: {recs}")
        else:
            log.critical("Recording parameters not found in cache")
            continue  # Skip rest of loop if recs not found

        rec_time_path = config['path']['out']['cache'] + '/rec_time'
        if file_exists(rec_time_path):
            with open(rec_time_path, 'r') as f:
                next_record_time = int(f.readline().strip())
                next_record_timestamp = f.readline().strip()
                log.info(f"Read next record time: {next_record_time} ({next_record_timestamp})")
        else:
            log.critical("Next record time not found in cache")
            continue  # Skip rest of loop if rec_time not found

        time_to_next_record = next_record_time - time()
        if time_to_next_record > config['time']['interval']['SM']['sampling'] * config['samples']['per_red']['SM'] + 3:
            log.info(f"Pausing for {time_to_next_record} seconds")
            pause(time_to_next_record)  

        # Read soil moisture
        if 'SM' in recs:
            log.info("Reading soil moisture")
            readings = read_sm(config['nsensors']['SM'])
            log.info("Writing soil moisture readings to records")
            with open(config['fpath']['sm'], 'a') as f:
                f.write(f"{next_record_timestamp}, " + ", ".join(str(readings[f'SM{n}']['mean']) for n in range(1, config['nsensors']['SM'] + 1)) + "\n")
            log.info("Soil moisture readings written to records")
        
        # TODO: Implement DHT11 reading
        if 'DHT11' in recs:
            log.info("Reading temperature and humidity")
            pass

        # Read internal temperature
        if 'ITEMP' in recs:
            log.info("Reading internal temperature")
            temperature = read_internal_temp()
            log.info("Writing internal temperature to data")
            with open(config['fpath']['itemp'], 'a') as f:
                f.write(f"{next_record_timestamp}, {temperature}\n")

        # Read battery voltage
        if 'BATT' in recs:
            log.info("Reading battery voltage")
            voltage, percentage = read_battery()
            log.info("Writing battery voltage to data")
            with open(config['fpath']['battery'], 'a') as f:
                f.write(f"{next_record_timestamp}, {voltage}, {percentage}\n")

        # Calculate next record time
        # FIXME: pause until the prev. record time to make sure that you are calculating the next record time and not the repeat the ts
        next_record_time, next_record_timestamp = prep_next_ts()
        led.off()
        time_to_next_record = next_record_time - time()
        if time_to_next_record > config['time']['wake_haste']:
            log.info(f"Sleeping until next record time: {strf_time(next_record_time, mode='time.time')}; for {time_to_next_record - config['time']['wake_haste']} seconds")
            sleep((time_to_next_record - config['time']['wake_haste']) * 1000)
            log.info("Woke up from sleep (@main). Resuming main loop.")
        else:
            log.info("Next record time is too close. Skipping sleep.")
            pause(time_to_next_record)
            log.info("Resuming main loop.")

    else:
        led.on()
        log.info("Recording turned off. Pausing for 60 seconds")
        pause(60)
        log.info("Resuming switch check")
        led.off()