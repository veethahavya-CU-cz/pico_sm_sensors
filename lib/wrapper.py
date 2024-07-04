# type: ignore
import sys, os
from machine import SoftI2C, Pin, SPI, ADC
from time import sleep as pause


sys.path.append('/lib/')

import logging as log
from helper import get_config, dir_exists

from sdcard import SDCard
from ds1307 import DS1307



def rtc_setup():
    config = get_config()

    log.debug('Defining I2C for RTC')
    rtc_i2c = SoftI2C(scl=Pin(config['Pin']['RTC']['SCL']), sda=Pin(config['Pin']['RTC']['SDA']), freq=1_00_000)
    log.debug('Scanning I2C for RTC')
    rtc_check = rtc_i2c.scan()

    if rtc_check == []:
        log.error('RTC not found')
        return None
    else:
        log.debug('RTC found at address: {}'.format(rtc_check[0]))
        return DS1307(rtc_i2c, 0x68)



def sd_mount():
    config = get_config()
    if not dir_exists(config['path']['sd_root']):
        try:
            log.debug('Defining SPI for SD Card')
            sd_spi = SPI(config['Pin']['SD']['BUS'], baudrate=1_000_000, polarity=0, phase=0, firstbit=SPI.MSB, sck=Pin(config['Pin']['SD']['SCK']), mosi=Pin(config['Pin']['SD']['MOSI']), miso=Pin(config['Pin']['SD']['MISO']))
            log.debug('Accessing SD Card via library')
            sd = SDCard(sd_spi, Pin(config['Pin']['SD']['CS']))
            log.debug('Mounting SD Card as FAT')
            vfs = os.VfsFat(sd)
            os.mount(vfs, config['path']['sd_root'])
            log.debug('SD Card mounted')
            return True
        except:
            return False
    else:
        log.warning('SD Card already mounted')
        return True

def sd_unmount():
    try:
        os.umount(config['path']['sd_root'])
        return True
    except:
        log.warning('Error unmounting SD Card. Already unmounted?')
        return False



def read_sm(nsensors):
    config = get_config()

    readings = {}
    for ns in range(1, nsensors+1):
        readings[f'SM{ns}'] = {}
        readings[f'SM{ns}']['raw'] = []
        for _ in range(config['samples']['per_red']['SM']):
            sm = ADC(config['ADC'][f'SM{ns}'])
            readings[f'SM{ns}']['raw'].append(sm.read_u16())
            pause(config['time']['interval']['SM']['sampling'])
        readings[f'SM{ns}']['mean'] = sum(readings[f'SM{ns}']['raw']) / len(readings[f'SM{ns}']['raw'])

    return readings


def read_internal_temp():
    config = get_config()

    try:
        temp = ADC(ADC.CORE_TEMP)
    except:
        try:
            temp = ADC(config['ADC']['CORE_TEMP'])
        except:
            log.critical('Temperature sensor not found')

    readings = []
    for _ in range(config['samples']['per_red']['INTERNAL_TEMP']):
        readings.append(temp.read_u16())
        pause(config['time']['interval']['INTERNAL_TEMP']['sampling'])

    voltage = sum(readings) / len(readings)
    temperature = 27 - (ADC(4).read_u16() * (3.3 / 2**16) - 0.706) / 0.001721

    return temperature


def read_battery():
    config = get_config()
    
    batt = ADC(config['ADC']['VSYS'])
    readings = []

    for _ in range(config['samples']['per_red']['VSYS']):
        readings.append(batt.read_u16())
        pause(config['time']['interval']['VSYS']['sampling'])

    voltage = sum(readings) / len(readings)
    battery_voltage = voltage * ((3*3.3) / 2**16)
    battery_percentage = (battery_voltage - 3.2) / (4.2 - 3.3) * 100

    return battery_voltage, battery_percentage