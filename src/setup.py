from machine_config import CONFIG

from usys import path as sys_path
from uos import mkdir
from machine import RTC
from utime import gmtime
from ujson import dump as dump_json

from os import path
from upysh import cp

sys_path.append('/usr/lib')
import picostation_logging as log
from picostation_wrapper import rtc_setup, sd_mount, status_led


def read_station_metadata():
    try:
        # Read datetime from file
        with open('./datetime.txt', 'r') as file:
            dt = file.read().strip()
        CONFIG['datetime'] = tuple(eval(dt))
    except:
        CONFIG['datetime'] = None

    # Read station ID, location and notes from file
    station_metadata = {}
    with open('./station.txt', 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            station_metadata[key] = value

    CONFIG['ID'] = int(station_metadata['sid'])
    CONFIG['LOC'] = station_metadata['loc']
    CONFIG['NOTES'] = station_metadata['notes']


# Dump configuration to file
def dump_config():
    log.info("Dumping configuration to file: /config.json")
    with open('/config.json', 'w') as f:
        dump_json(CONFIG, f)
    with open('/ID', 'w') as f:
        f.write(str(CONFIG['ID']))
    with open('/LOC', 'w') as f:
        f.write(CONFIG['LOC'])
    with open('/NOTES', 'w') as f:
        f.write(CONFIG['NOTES'])
    log.info("Configuration dumped")


# Setup Logging
def setup_logging():
    if CONFIG['IO']['log']['UART']:
        uart_out = [
            CONFIG['Pin']['UART']['BUS'],
            CONFIG['time']['interval']['UART_BAUD'],
            CONFIG['Pin']['UART']['TX'],
            CONFIG['Pin']['UART']['RX'],
        ]
    else:
        uart_out = None
    log.init(file='/sys.log', lvl=CONFIG['IO']['log']['level'], rewrite=True, uart_out=uart_out)


# Check if necessary source and library files exist
def check_files():
    log.info("Checking if necessary source and library files exist")
    for file in CONFIG['files']['src']:
        if not path.exists(path.join(CONFIG['path']['src'], file)):
            log.error(f"Source file '{file}' not found in '{CONFIG['path']['src']}'")
            raise ValueError(f"Source file '{file}' not found in '{CONFIG['path']['src']}'")
        
    for file in CONFIG['files']['lib']:
        if not path.exists(path.join(CONFIG['path']['lib'], file)):
            log.error(f"Library file '{file}' not found in '{CONFIG['path']['lib']}'")
            raise ValueError(f"Library file '{file}' not found in '{CONFIG['path']['lib']}'")
        
    for file in CONFIG['files']['usr-lib']:
        if not path.exists(path.join(CONFIG['path']['usr-lib'], file)):
            log.error(f"Library file '{file}' not found in '{CONFIG['path']['usr-lib']}'")
            raise ValueError(f"Library file '{file}' not found in '{CONFIG['path']['usr-lib']}'")
    log.info("All necessary source and library files found")


# Setup RTC
def setup_rtc():
    try:
        log.info("Setting up RTC")
        clock = rtc_setup()
        log.info("RTC setup complete")
        log.info("Updating RTC time")
        if CONFIG['datetime']:
            clock.datetime = CONFIG['datetime']
            log.info(f"RTC time updated to: {clock.datetime}")
            log.info("Updating machine time")
            internal_clock = RTC()
            internal_clock.datetime((clock.year, clock.month, clock.day, clock.weekday, clock.hour, clock.minute, clock.second, 0))
            log.info(f"Machine time updated to: {internal_clock.datetime()}")
        else:
            log.warning(f"RTC time not provided. Using machine time: {gmtime()}.")
            clock.datetime = gmtime()
        if clock.halt:
            log.info("Clock was halted. Enabling RTC oscillator.")
            clock.halt = False
            log.debug("RTC oscillator enabled.")
        return clock
    except Exception as e:
        status_led('flash/error_rtc')
        log.error(f"Failed to setup RTC: {e}")
        raise RuntimeError("Failed to setup RTC")


# Setup SD Card
def setup_sd_card():
    log.info("Mounting SD Card")

    if not sd_mount():
        log.error("SD Card could not be mounted")
        status_led('flash/error_sd')
        raise RuntimeError("SD Card could not be mounted")
    log.info("SD Card mounted")


# Create necessary output directories
def create_output_dirs():
    log.info("Creating necessary output directories")
    for key, outpath in CONFIG['path']['out'].items():
        if not path.exists(outpath):
            log.info(f"Creating directory: {outpath}")
            mkdir(outpath)
    log.info("All necessary output directories created")


# Create necessary output files
def create_output_files():
    log.info("Creating necessary output files")
    with open(CONFIG['fpath']['sm'], 'w') as f:
        f.write("Time,SM1,SM2,SM3\n")
    with open(CONFIG['fpath']['meteo'], 'w') as f:
        f.write("Time,Temperature,Humidity\n")
    with open(CONFIG['fpath']['itemp'], 'w') as f:
        f.write("Time,Internal Temperature\n")
    with open(CONFIG['fpath']['battery'], 'w') as f:
        f.write("Time,Battery Voltage, Battery Percentage\n")
    log.info("All necessary output files created")


# Main setup processes
setup_logging()
read_station_metadata()
dump_config()

status_led('busy')

check_files()

_ = setup_rtc()
setup_sd_card()
log.move_logfile(CONFIG['IO']['log']['file'], rewrite=True)

create_output_dirs()
create_output_files()

log.info("Copying configuration file to SD Card")
cp(CONFIG['fpath']['config'], path.join(CONFIG['path']['out']['config'], '/config.json'))
cp('/ID', path.join(CONFIG['path']['out']['config'], '/ID'))
cp('/LOC', path.join(CONFIG['path']['out']['config'], '/LOC'))
cp('/NOTES', path.join(CONFIG['path']['out']['config'], '/NOTES'))
log.info("Setup complete!")

status_led('flash/success')
status_led('off')