# type: ignore
import os, sys
from machine import RTC

import json


sys.path.append('/lib/')

import logging as log
from wrapper import rtc_setup, sd_mount
from helper import dir_exists, file_exists, cp


#################################################### CONFIGURATION ####################################################

# ACTIVE CONFIGURATION
year = 2024
month = 6
day = 6
hour = 8
minute = 1
second = 0
weekday = 1

ID = 1
LOC = ''
NOTES = ''
# END ACTIVE CONFIGURATION

config = {}
config['ID'] = ID
config['LOC'] = LOC
config['NOTES'] = NOTES

config['datetime'] = [year, month, day, hour, minute, second, weekday]

config['time'] = {}   # unit: seconds
config['time']['interval'] = {}
config['time']['wake_haste'] = 7

config['time']['interval']['SM'] = {}
config['time']['interval']['SM']['logging'] = 60 * 10
config['time']['interval']['SM']['sampling'] = 0.1

config['time']['interval']['DHT11'] = {}
config['time']['interval']['DHT11']['logging'] = None
config['time']['interval']['DHT11']['sampling'] = None

config['time']['interval']['INTERNAL_TEMP'] = {}
config['time']['interval']['INTERNAL_TEMP']['sampling'] = 0.1

config['time']['interval']['VSYS'] = {}
config['time']['interval']['VSYS']['sampling'] = 0.1


config['samples'] = {}
config['samples']['per_red'] = {}
config['samples']['per_red']['SM'] = 10
config['samples']['per_red']['DHT11'] = 5
config['samples']['per_red']['INTERNAL_TEMP'] = 7
config['samples']['per_red']['VSYS'] = 7


config['nsensors'] = {}
config['nsensors']['SM'] = 3
config['nsensors']['DHT11'] = 1

config['Pin'] = {}
config['Pin']['led'] = 25
config['Pin']['RTC'] = {'SCL': 7, 'SDA': 6}
config['Pin']['SD'] = {'BUS': 0, 'SCK': 2, 'MOSI': 3, 'MISO': 4, 'CS': 5}
config['Pin']['DHT11'] = 20

config['ADC'] = {}
config['ADC']['SM1'] = 0
config['ADC']['SM2'] = 1
config['ADC']['SM3'] = 2
config['ADC']['VSYS'] = 3
config['ADC']['temperature'] = 4


config['depth'] = {}   # unit: cm
config['depth']['SM1'] = 15
config['depth']['SM2'] = 40
config['depth']['SM3'] = 60


config['format'] = {}
config['format']['time'] = '%Y-%m-%d %H:%M:%S'

config['IO'] = {}
config['IO']['ITEMP'] = True   # Record Internal Temperature
config['IO']['BATT'] = True   # Record Battery Voltage/Percentage
config['IO']['log'] = {}
config['IO']['log']['file'] = 'sys.log'
config['IO']['log']['level'] = 'DEBUG'   # DEBUG, INFO, WARNING, ERROR, CRITICAL


config['path'] = {}
config['fpath'] = {}
config['files'] = {}

config['path']['src'] = '/'
config['path']['lib'] = '/lib/'
config['files']['src'] = ['setup.py', 'boot.py', 'main.py']
config['files']['lib'] = ['helper.py', 'logging.py', 'wrapper.py', 'ds1307.py', 'sdcard.py', 'dht11.py']

config['path']['sd_root'] = '/sd'   # not modifiable
config['path']['out'] = {}
config['path']['out']['root'] = config['path']['sd_root']

# derived paths
config['path']['out']['records'] = config['path']['out']['root'] + '/' + 'records'
config['path']['out']['config'] = config['path']['out']['root'] + '/' + '.config'
config['path']['out']['cache'] = config['path']['out']['root'] + '/' + '.cache'
config['path']['out']['data'] = config['path']['out']['root'] + '/' + 'data'

config['fpath']['config'] = 'config.json'
config['fpath']['log'] = config['path']['out']['root'] + '/' + config['IO']['log']['file']
config['fpath']['sm'] = config['path']['out']['records'] + '/' + 'sm'
config['fpath']['sm_raw'] = config['path']['out']['records'] + '/' + 'sm'
config['fpath']['meteo'] = config['path']['out']['records'] + '/' + 'meteo'
config['fpath']['itemp'] = config['path']['out']['data'] + '/' + 'itemp'
config['fpath']['battery'] = config['path']['out']['data'] + '/' + 'battery'

################################################## END CONFIGURATION ##################################################

### Setup Logging
log.init(file='/sys.log', lvl=config['IO']['log']['level'], rewrite=True)


### Dump configuration to file
log.info("Dumping configuration to file: /config.json")
with open('/config.json', 'w') as f:
    json.dump(config, f)
with open('/ID', 'w') as f:
    f.write(str(ID))
with open('/LOC', 'w') as f:
    f.write(LOC)
with open('/NOTES', 'w') as f:
    f.write(NOTES)
log.info("Configuration dumped")


### Check if necessary source and library files exist
log.info("Checking if necessary source and library files exist")

for file in config['files']['src']:
    if not file_exists(config['path']['src'] + '/' + file):
        log.error(f"Source file '{file}' not found in '{config['path']['src']}'")
        raise Exception(f"Source file '{file}' not found in '{config['path']['src']}'")

for file in config['files']['lib']:
    if not file_exists(config['path']['lib'] + '/' + file):
        log.error(f"Library file '{file}' not found in '{config['path']['lib']}'")
        raise Exception(f"Library file '{file}' not found in '{config['path']['lib']}'")

log.info("All necessary source and library files found")


### Setup RTC
log.info("Setting up RTC")
clock = rtc_setup()
log.info("RTC setup complete")

log.info("Updating RTC time")
clock.datetime = (config['datetime'][0], config['datetime'][1], config['datetime'][2], config['datetime'][3], config['datetime'][4], config['datetime'][5], config['datetime'][6], None)
log.info("RTC time updated")
log.info("RTC time: {}".format(clock.datetime))

if clock.disable_oscillator:
    log.info("Enabling RTC oscillator")
    clock.disable_oscillator = False
    log.info("RTC oscillator enabled.")

log.info("Updating machine time")
RTC().datetime(clock.datetimeRTC)
log.info(f"Machine time updated. Machine time: {RTC().datetime()}")


### Setup SD Card
log.info("Mounting SD Card")

check = sd_mount()
if not check:
    log.error("SD Card could not be mounted")
    raise Exception("SD Card could not be mounted")

log.info("SD Card mounted")


### Create necessary output directories
for key, value in config['path']['out'].items():
    if not dir_exists(value):
        log.info(f"Creating directory: {value}")
        os.mkdir(value)
log.info("All necessary output directories created")

### Create necessary output files
log.info("Creating necessary output files")
with open(config['fpath']['sm'], 'w') as f:
    f.write(f"Time,SM1,SM2,SM3\n")
with open(config['fpath']['meteo'], 'w') as f:
    f.write(f"Time,Temperature,Humidity\n")
with open(config['fpath']['itemp'], 'w') as f:
    f.write(f"Time,Internal Temperature\n")
with open(config['fpath']['battery'], 'w') as f:
    f.write(f"Time,Battery Voltage, Battery Percentage\n")
log.info("All necessary output files created")


log.move(config['fpath']['log'], rewrite=True)

log.info("Copying configuration file to SD Card")
cp(config['fpath']['config'], config['path']['out']['config'] + '/config.json')
cp('/ID', config['path']['out']['config'] + '/ID')
cp('/LOC', config['path']['out']['config'] + '/LOC')
cp('/NOTES', config['path']['out']['config'] + '/NOTES')


### Create necessary output directories
for key, value in config['path']['out'].items():
    if not dir_exists(value):
        log.info(f"Creating directory: {value}")
        os.mkdir(value)
log.info("All necessary output directories created")