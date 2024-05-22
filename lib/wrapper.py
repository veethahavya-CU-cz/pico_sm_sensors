# type: ignore
import sys, os
import json
from machine import SoftI2C, Pin, SPI

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
        return None
        log.error('RTC not found')
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