from usys import path as sys_path
from utime import time
from utime import sleep as pause
from machine import reset
from machine import RTC, Pin
from machine import lightsleep as sleep

from os import path
from rp2 import bootsel_button as switch

sys_path.insert(0, '/usr/lib')
import picostation_logging as log
from picostation_wrapper import rtc_setup, sd_mount   #, status_led
from picostation_wrapper import read_sm, read_dht11, read_internal_temp, read_battery
from picostation_wrapper import write_sm, write_dht11, write_internal_temp, write_battery
from picostation_helper import get_config, prep_next_ts


# Read config file
CONFIG = get_config()
#status_led('busy')

pfm = Pin(23)
pfm.high()

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
        #status_led('flash/error_rtc')
        log.error(f"Failed to setup RTC: {e}")
        raise RuntimeError("Failed to setup RTC")

# Mount SD Card
if not path.exists(CONFIG['path']['sd_root']):
    log.debug("Mounting SD Card")
    if not sd_mount():
        #status_led('flash/error_sd')
        log.error("SD Card could not be mounted")
        raise Exception("SD Card could not be mounted")
    log.info("SD Card mounted")


# Data Recording and Logging setup
#TODO: report values via UART
while True:
    # if logger_switch.value():
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
        log.critical("Next record time not found in cache.\nRe-booting the station controller...")
        reset()

    time_to_record = cur_record_time - time()
    ##############################################################################################################################################
    log.debug(f"Current time: {time()} & Current record time: {cur_record_time}")
    log.debug(f"Time to next record: {time_to_record}")
    # if time_to_record > CONFIG['time']['interval']['SM']['sampling'] * CONFIG['samples']['per_red']['SM'] + 3:
    #     log.debug(f"Too early. Pausing for {time_to_record} seconds")
    #     pause(time_to_record)
    if time_to_record > 0 and time_to_record < CONFIG['time']['interval']['SM']['logging']:
        log.debug(f"Pausing for {time_to_record} seconds")
        pause(time_to_record)
        #FIXME: pause only if time_to_record <= wake_haste; else sleep and then update machine time from RTC just to confirm
    elif time_to_record < 0:
        reset()
    elif time_to_record < CONFIG['time']['interval']['SM']['logging']:
        reset()
    ##############################################################################################################################################

    #status_led('measuring')
    # Read soil moisture
    if 'SM' in recs:
        #status_led('flash/busy_measuring', var='SM')
        log.debug("Reading soil moisture")
        readings = read_sm(CONFIG['nsensors']['SM'])
        log.debug("Writing soil moisture readings to records")
        write_sm(readings, cur_record_timestamp, raw=True)
        log.info("Soil moisture readings written to records")
        #status_led('flash/success_measuring')

    # Read temperature and humidity (DHT11)
    if 'DHT11' in recs:
        #status_led('flash/busy_measuring', var='DHT11')
        log.debug("Reading temperature and humidity")
        temp, humd = read_dht11()
        log.debug("Writing temperature and humidity to records")
        write_dht11(temp, humd, cur_record_timestamp)
        log.info("Temperature and humidity written to records")
        #status_led('flash/success_measuring')

    # Read internal temperature
    if 'ITEMP' in recs:
        #status_led('flash/busy_measuring', var='ITEMP')
        log.debug("Reading internal temperature")
        temperature = read_internal_temp()
        log.debug("Writing internal temperature to data")
        write_internal_temp(temperature, cur_record_timestamp)
        log.info("Internal temperature written to data")
        #status_led('flash/success_measuring')

    # Read battery voltage
    if 'BATT' in recs:
        #status_led('flash/busy_measuring', var='BATT')
        log.debug("Reading battery voltage")
        voltage, percentage = read_battery()
        log.debug("Writing battery voltage to data")
        write_battery(voltage, percentage, cur_record_timestamp)
        log.info("Battery voltage written to data")
        #status_led('flash/success_measuring')

    #status_led('busy')
    # log.debug(f"Current time: {time()} & Current record time: {cur_record_time}")
    # if time() < cur_record_time:
    #     #status_led('flash/idle')
    #     log.info(f"Waiting for current recording time to elapse. Pausing for {cur_record_time - time() + 1} seconds")
    #     pause(cur_record_time - time() + 1)

    #status_led('busy')
    next_record_time, next_record_timestamp = prep_next_ts()
    time_to_record = next_record_time - time()
    if time_to_record > CONFIG['time']['wake_haste']:
        log.info(
            f"Sleeping until next record time: {next_record_timestamp}; for {time_to_record - CONFIG['time']['wake_haste']} seconds"
        )
        #status_led('flash/idle')
        pause(CONFIG['time']['sleep_buffer_pause'])
        sleep((time_to_record - CONFIG['time']['wake_haste']) * 1000)
        #status_led('busy')
        log.info("Woke up from sleep (@main)")
        log.info("Updating machine time")
        internal_clock = RTC()
        internal_clock.datetime((clock.year, clock.month, clock.day, clock.weekday, clock.hour, clock.minute, clock.second, 0))
        log.info(f"Machine time updated: {RTC().datetime()}")
        log.info("Resuming main loop.")
    else:
        log.info("Next record time is too close. Skipping sleep.")
        #status_led('flash/idle')
        #status_led('off')
        pause(time_to_record)
        log.info("Resuming main loop.")

# else:
#     #status_led('idle')

#     led.on()
#     log.info("Recording turned off. Pausing for 15 seconds")
#     pause(15)
#     log.info("Resuming switch check")
#     led.off()
