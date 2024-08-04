# type: ignore
import config
from usys import path
from uos import mkdir
from machine import RTC
from ujson import dump as dump_json

path.append('/lib/')
import logging as log
from wrapper import rtc_setup, sd_mount
from helper import dir_exists, file_exists, cp



### Setup Logging
if CONFIG['IO']['log']['UART']:
    uart_out = [CONFIG['Pin']['UART']['BUS'], CONFIG['time']['interval']['UART_BAUD'], CONFIG['Pin']['UART']['TX'], CONFIG['Pin']['UART']['RX']]
else:
    uart_out = None
log.init(file=CONFIG['IO']['log']['file'], lvl=CONFIG['IO']['log']['level'], rewrite=True, uart_out=uart_out)

### Dump configuration to file
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

### Check if necessary source and library files exist
def check_files():
    log.info("Checking if necessary source and library files exist")
    for file in CONFIG['files']['src']:
        if not file_exists(CONFIG['path']['src'] + '/' + file):
            log.error(f"Source file '{file}' not found in '{CONFIG['path']['src']}'")
            raise ValueError(f"Source file '{file}' not found in '{CONFIG['path']['src']}'")
    for file in CONFIG['files']['lib']:
        if not file_exists(CONFIG['path']['lib'] + '/' + file):
            log.error(f"Library file '{file}' not found in '{CONFIG['path']['lib']}'")
            raise ValueError(f"Library file '{file}' not found in '{CONFIG['path']['lib']}'")
    log.info("All necessary source and library files found")


### Setup RTC
def setup_rtc():
    log.info("Setting up RTC")
    clock = rtc_setup()
    log.info("RTC setup complete")
    log.info("Updating RTC time")
    clock.datetime = tuple(CONFIG['datetime'] + [None])
    log.info(f"RTC time updated to: {clock.datetime}")
    if clock.disable_oscillator:
        log.info("Enabling RTC oscillator")
        clock.disable_oscillator = False
        log.info("RTC oscillator enabled.")
    log.info("Updating machine time")
    internal_clock = RTC()
    internal_clock.datetime(clock.datetimeRTC)
    log.info(f"Machine time updated to: {internal_clock.datetime()}")
    return clock

### Setup SD Card
def setup_sd_card():
    log.info("Mounting SD Card")
    if not sd_mount():
        log.error("SD Card could not be mounted")
        raise RuntimeError("SD Card could not be mounted")
    log.info("SD Card mounted")


### Create necessary output directories
def create_output_dirs():
    log.info("Creating necessary output directories")
    for key, path in CONFIG['path']['out'].items():
        if not dir_exists(path):
            log.info(f"Creating directory: {path}")
            mkdir(path)
    log.info("All necessary output directories created")

### Create necessary output files
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


### Main setup process
def main_setup():
    dump_config()
    check_files()
    _ = setup_rtc()
    setup_sd_card()
    create_output_dirs()
    create_output_files()

    log.move(CONFIG['fpath']['log'], rewrite=True)
    log.info("Copying configuration file to SD Card")
    cp(CONFIG['fpath']['config'], CONFIG['path']['out']['config'] + '/config.json')
    cp('/ID', CONFIG['path']['out']['config'] + '/ID')
    cp('/LOC', CONFIG['path']['out']['config'] + '/LOC')
    cp('/NOTES', CONFIG['path']['out']['config'] + '/NOTES')
    log.info("Setup complete!")

if __name__ == "__main__":
    main_setup()