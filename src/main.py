from usys import path as sys_path
from utime import time
from utime import sleep as pause
from machine import reset
from machine import RTC, Pin
from machine import lightsleep as sleep

from os import path

sys_path.insert(0, '/usr/lib')
import picostation_logging as log
from picostation_wrapper import rtc_setup, sd_mount, read_sm, read_dht11, read_internal_temp, read_battery, status_led
from picostation_helper import get_config, prep_next_ts


# Read config file
CONFIG = get_config()
status_led('busy')

led = Pin('LED', Pin.OUT)
logger_switch = Pin(CONFIG['Pin']['logger_switch'], Pin.IN)

# Setup RTC
if 'clock' not in globals():
    try:
        log.debug("Setting up RTC")
        clock = rtc_setup()
        log.info("RTC setup complete")

        log.debug("Updating machine time")
        RTC().datetime((clock.year, clock.month, clock.day, clock.weekday, clock.hour, clock.minute, clock.second, 0))
        log.info(f"Machine time updated: {RTC().datetime()}")
    except Exception as e:
        status_led('flash/error_rtc')
        log.error(f"Failed to setup RTC: {e}")
        raise RuntimeError("Failed to setup RTC")

# Mount SD Card
if not path.exists(CONFIG['path']['sd_root']):
    log.debug("Mounting SD Card")
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
        recs_path = path.join(CONFIG['path']['out']['cache'], 'recs')
        if path.exists(recs_path):
            with open(recs_path, 'r') as f:
                recs = f.read().splitlines()
                log.debug(f"Read recording parameters: {recs}")
        else:
            log.critical("Recording parameters not found in cache\nRe-booting the station controller...")
            reset()

        rec_time_path = path.join(CONFIG['path']['out']['cache'], 'rec_time')
        if path.exists(rec_time_path):
            with open(rec_time_path, 'r') as f:
                cur_record_time = int(f.readline().strip())
                cur_record_timestamp = f.readline().strip()
                log.debug(f"Read current record time: {cur_record_time} ({cur_record_timestamp})")
        else:
            log.critical("Next record time not found in cache")
            reset()

        time_to_next_record = cur_record_time - time()
        if time_to_next_record > CONFIG['time']['interval']['SM']['sampling'] * CONFIG['samples']['per_red']['SM'] + 3:
            log.debug(f"Too early. Pausing for {time_to_next_record} seconds")
            pause(time_to_next_record)

        status_led('measuring')
        # Read soil moisture
        if 'SM' in recs:
            status_led('flash/busy_measuring', var='SM')
            log.debug("Reading soil moisture")
            readings = read_sm(CONFIG['nsensors']['SM'])
            log.debug("Writing soil moisture readings to records")

            with open(CONFIG['fpath']['sm'], 'a') as f:
                f.write(
                    f"{cur_record_timestamp}, "
                    + ", ".join(str(readings[f'SM{n}']['mean']) for n in range(1, CONFIG['nsensors']['SM'] + 1))
                    + "\n"
                )
            log.info("Soil moisture readings written to records")
            log.debug("Writing raw soil moisture readings to data")
            with open(CONFIG['fpath']['sm_raw'], 'a') as f:
                f.write(
                    f"{cur_record_timestamp}, "
                    + ", ".join(str(readings[f'SM{n}']['raw']) for n in range(1, CONFIG['nsensors']['SM'] + 1))
                    + "\n"
                )
            log.info("Raw soil moisture readings written to data")
            status_led('flash/success_measuring')

        # Read temperature and humidity (DHT11)
        if 'DHT11' in recs:
            status_led('flash/busy_measuring', var='DHT11')
            log.debug("Reading temperature and humidity")
            temp, humd = read_dht11()
            log.debug("Writing temperature and humidity to records")
            with open(CONFIG['fpath']['meteo'], 'a') as f:
                f.write(f"{cur_record_timestamp}, {temp}, {humd}\n")
            log.info("Temperature and humidity written to records")
            status_led('flash/success_measuring')

        # Read internal temperature
        if 'ITEMP' in recs:
            status_led('flash/busy_measuring', var='ITEMP')
            log.debug("Reading internal temperature")
            temperature = read_internal_temp()
            log.debug("Writing internal temperature to data")
            with open(CONFIG['fpath']['itemp'], 'a') as f:
                f.write(f"{cur_record_timestamp}, {temperature}\n")
            log.info("Internal temperature written to data")
            status_led('flash/success_measuring')

        # Read battery voltage
        if 'BATT' in recs:
            status_led('flash/busy_measuring', var='BATT')
            log.debug("Reading battery voltage")
            voltage, percentage = read_battery()
            log.debug("Writing battery voltage to data")
            with open(CONFIG['fpath']['battery'], 'a') as f:
                f.write(f"{cur_record_timestamp}, {voltage}, {percentage}\n")
            log.info("Battery voltage written to data")
            status_led('flash/success_measuring')

        status_led('busy')
        log.debug(f"Current time: {time()} & Current record time: {cur_record_time}")
        if time() < cur_record_time:
            status_led('flash/idle')
            log.info(f"Waiting for current recording time to elapse. Pausing for {cur_record_time - time() + 1} seconds")
            pause(cur_record_time - time() + 1)

        status_led('busy')
        next_record_time, next_record_timestamp = prep_next_ts()
        time_to_next_record = next_record_time - time()
        if time_to_next_record > CONFIG['time']['wake_haste']:
            log.info(
                f"Sleeping until next record time: {next_record_timestamp}; for {time_to_next_record - CONFIG['time']['wake_haste']} seconds"
            )
            status_led('flash/idle')
            pause(CONFIG['time']['sleep_buffer_pause'])
            sleep((time_to_next_record - CONFIG['time']['wake_haste']) * 1000)
            status_led('busy')
            log.info("Woke up from sleep (@main). Resuming main loop.")
        else:
            log.info("Next record time is too close. Skipping sleep.")
            status_led('flash/idle')
            status_led('off')
            pause(time_to_next_record)
            log.info("Resuming main loop.")

    else:
        status_led('idle')
        led.on()
        log.info("Recording turned off. Pausing for 15 seconds")
        pause(15)
        log.info("Resuming switch check")
        led.off()
