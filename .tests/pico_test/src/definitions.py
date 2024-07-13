from machine import Pin, ADC
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL


####### TIME DEFINITIONS #######
sm_logging_interval = 60 * 10  # 10 minutes
sm_n_samples_per_log = 10
sm_sampling_interval = 0.1

dht11_logging_interval_global = 60 * 10  # 10 minutes
dht11_n_samples_per_log = 10
dht11_sampling_interval = 0.1


####### PIN DEFINITIONS #######
led = Pin("LED", Pin.OUT)

sm_sensor_power = Pin(21, Pin.OUT)
dht11_sensor_power = Pin(22, Pin.OUT)

sm_15_sensor = ADC(0)
sm_40_sensor = ADC(1)
sm_60_sensor = ADC(2)

dht11_sensor = Pin(20, Pin.IN, Pin.PULL_UP)

sd_card_SPI_bus = 0
####### FILE DEFINITIONS #######
outfiles = ['sm.txt', 'temp.txt', 'rh.txt']
logfile = 'log.txt'


####### I/O DEFINITIONS #######
logging_level = INFO