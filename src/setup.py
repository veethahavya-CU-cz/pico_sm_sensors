# type: ignore
import sys
import json

from helper import dir_exists, file_exists, get_logger

sys.path.append('/lib/')
import logging
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL
from wrapper import rtc_setup, sd_mount


#################################################### CONFIGURATION ####################################################

config = {}

config['datetime'] = [2024, 5, 21, 14, 0, 0, 0, 1]   # year, month, day, hour, minute, second, weekday: integer: 0-6

config['time'] = {}   # unit: seconds
config['time']['interval'] = {}

config['time']['interval']['SM'] = {}
config['time']['interval']['SM']['logging'] = 60 * 10
config['time']['interval']['SM']['sampling'] = 0.1

config['time']['interval']['DHT11'] = {}
config['time']['interval']['DHT11']['logging'] = 60 * 30
config['time']['interval']['DHT11']['sampling'] = 1


config['samples'] = {}
config['samples']['SM_per_log'] = 10
config['samples']['DHT11_per_log'] = 5


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

config['IO'] = {}
config['IO']['log'] = {}
config['IO']['log']['file'] = 'sys.log'
config['IO']['log']['level'] = INFO


config['path'] = {}
config['fpath'] = {}
config['files'] = {}

config['path']['sd_mnt'] = '/sd0/'
config['path']['out'] = {}
config['path']['src'] = '/src/'
config['path']['lib'] = '/lib/'
config['path']['out']['root'] = config['path']['sd_mnt']

config['files']['src'] = ['helper.py', 'setup.py', 'boot.py', 'main.py']
config['files']['lib'] = ['logging.py', 'wrapper.py', 'ds1307.py', 'sdcard.py', 'dht11.py']

# derived paths
config['path']['out']['records'] = config['path']['out']['root'] + '/' + 'records' + '/'
config['path']['out']['config'] = config['path']['out']['root'] + '/' + 'config' + '/'
config['path']['out']['cache'] = config['path']['out']['root'] + '/' + 'cache' + '/'
config['path']['out']['data'] = config['path']['out']['root'] + '/' + 'data' + '/'

config['fpath']['config'] = '/config.json'
config['fpath']['sm'] = config['path']['out']['records'] + '/' + 'sm'
config['fpath']['meteo'] = config['path']['out']['records'] + '/' + 'meteo'
config['fpath']['log'] = config['path']['out']['root'] + '/' + config['IO']['log']['file']

################################################## END CONFIGURATION ##################################################

### Setup Logging
log = logging.getLogger(__name__)
log.setLevel(config['IO']['log']['level'])
file_handler = logging.FileHandler('/sys.log', mode='w')
file_handler.setLevel(config['IO']['log']['level'])
formatter = logging.Formatter("%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
log.addHandler(file_handler)


log.info("Dumping configuration to file: /config.json")
with open('/config.json', 'w') as f:
    json.dump(config, f)
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
log.info('RTC time: {}'.format(clock.datetime))

log.info("Enabling RTC oscillator")
clock.disable_oscillator = False
log.info("RTC oscillator enabled")


### Setup SD Card
log.info("Mounting SD Card")
check = sd_mount()
if not check:
    log.error("SD Card could not be mounted")
    raise Exception("SD Card could not be mounted")
log.info("SD Card mounted")


### Create necessary output directories
log.info("Creating necessary output directories")
for key, value in config['path']['out'].items():
    if not dir_exists(value):
        print(value)
        log.info(f"Creating directory: {value}")
        os.mkdir(value)
log.info("All necessary output directories created")