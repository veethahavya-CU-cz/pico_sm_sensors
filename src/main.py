from usys import path as sys_path
from utime import time
from utime import sleep as pause
from machine import RTC, Pin
from machine import lightsleep as sleep

from os import path

sys_path.append('/usr/lib')
import picostation_logging as log
from picostation_wrapper import rtc_setup, sd_mount, read_sm, read_dht11, read_internal_temp, read_battery, status_led
from picostation_helper import get_config, prep_next_ts


# Read config file
config = get_config()
status_led('busy')

led = Pin('LED', Pin.OUT)
logger_switch = Pin(config['Pin']['logger_switch'], Pin.IN)

# Setup RTC
if 'clock' not in globals():
    try:
        log.info("Setting up RTC")
        clock = rtc_setup()
        log.info("RTC setup complete")

        log.info("Updating machine time")
        RTC().datetime((clock.year, clock.month, clock.day, clock.weekday, clock.hour, clock.minute, clock.second, 0))
        log.info(f"Machine time updated: {RTC().datetime()}")
    except Exception as e:
        status_led('flash/error_rtc')
        log.error(f"Failed to setup RTC: {e}")
        raise RuntimeError("Failed to setup RTC")

# Mount SD Card
if not path.exists(config['path']['sd_root']):
    log.info("Mounting SD Card")
    if not sd_mount():
        status_led('flash/error_sd')
        log.error("SD Card could not be mounted")
        raise Exception("SD Card could not be mounted")
    log.info("SD Card mounted")


# Logging setup
while True:
    if logger_switch.value():
        for _ in range(7):
            led.on()
            pause(0.1)
            led.off()
            pause(0.1)

        # Read recording parameters
        recs_path = config['path']['out']['cache'] + '/recs'
        if path.exists(recs_path):
            with open(recs_path, 'r') as f:
                recs = f.read().splitlines()
                log.info(f"Read recording parameters: {recs}")
        else:
            log.critical("Recording parameters not found in cache")
            continue  # Skip rest of loop if recs not found

        rec_time_path = config['path']['out']['cache'] + '/rec_time'
        if path.exists(rec_time_path):
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

        status_led('measuring')
        # Read soil moisture
        if 'SM' in recs:
            status_led('flash/busy_measuring', var='SM')
            log.info("Reading soil moisture")
            readings = read_sm(config['nsensors']['SM'])
            log.info("Writing soil moisture readings to records")

            with open(config['fpath']['sm'], 'a') as f:
                f.write(
                    f"{next_record_timestamp}, "
                    + ", ".join(str(readings[f'SM{n}']['mean']) for n in range(1, config['nsensors']['SM'] + 1))
                    + "\n"
                )
            log.info("Soil moisture readings written to records")
            log.info("writing raw soil moisture readings to records")
            with open(config['fpath']['sm_raw'], 'a') as f:
                f.write(
                    f"{next_record_timestamp}, "
                    + ", ".join(str(readings[f'SM{n}']['raw']) for n in range(1, config['nsensors']['SM'] + 1))
                    + "\n"
                )
            status_led('flash/success_measuring')

        # Read temperature and humidity (DHT11)
        if 'DHT11' in recs:
            status_led('flash/busy_measuring', var='DHT11')
            log.info("Reading temperature and humidity")
            temp, humd = read_dht11()
            log.info("Writing temperature and humidity to records")
            with open(config['fpath']['meteo'], 'a') as f:
                f.write(f"{next_record_timestamp}, {temp}, {humd}\n")
            log.info("Temperature and humidity written to records")
            status_led('flash/success_measuring')

        # Read internal temperature
        if 'ITEMP' in recs:
            status_led('flash/busy_measuring', var='ITEMP')
            log.info("Reading internal temperature")
            temperature = read_internal_temp()
            log.info("Writing internal temperature to data")
            with open(config['fpath']['itemp'], 'a') as f:
                f.write(f"{next_record_timestamp}, {temperature}\n")
            status_led('flash/success_measuring')

        # Read battery voltage
        if 'BATT' in recs:
            status_led('flash/busy_measuring', var='BATT')
            log.info("Reading battery voltage")
            voltage, percentage = read_battery()
            log.info("Writing battery voltage to data")
            with open(config['fpath']['battery'], 'a') as f:
                f.write(f"{next_record_timestamp}, {voltage}, {percentage}\n")
            status_led('flash/success_measuring')

        status_led('busy')
        # Calculate next record time
        if time() <= next_record_time:
            status_led('idle')
            pause(next_record_time - time() + 1)

        status_led('busy')
        next_record_time, next_record_timestamp = prep_next_ts()
        time_to_next_record = next_record_time - time()
        if time_to_next_record > config['time']['wake_haste']:
            log.info(
                f"Sleeping until next record time: {next_record_timestamp}; for {time_to_next_record - config['time']['wake_haste']} seconds"
            )
            status_led('flash/idle')
            sleep((time_to_next_record - config['time']['wake_haste']) * 1000)
            status_led('busy')
            log.info("Woke up from sleep (@main). Resuming main loop.")
        else:
            log.info("Next record time is too close. Skipping sleep.")
            status_led('idle')
            pause(time_to_next_record)
            log.info("Resuming main loop.")

    else:
        status_led('idle')
        led.on()
        log.info("Recording turned off. Pausing for 60 seconds")
        pause(3)
        log.info("Resuming switch check")
        led.off()
