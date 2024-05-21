# type: ignore

import sys
import json
import uos
import logging as log
from machine import SoftI2C, Pin, SPI

sys.path.append('/lib/')
from sdcard import SDCard
from ds1307 import DS1307
from helper import get_config, get_logger



def rtc_setup():
    config = get_config()
    rtc_i2c = SoftI2C(scl=Pin(config['Pin']['RTC']['SCL']), sda=Pin(config['Pin']['RTC']['SDA']), freq=1_00_000)
    rtc_check = rtc_i2c.scan()

    if rtc_check == []:
        return None
    else:
        return DS1307(rtc_i2c, 0x68)


def sd_mount():
    with open('/config.json', 'r') as config_file:
        config = json.load(config_file)
    try:
        sd_spi = SPI(config['Pin']['SD']['BUS'], baudrate=1_000_000, polarity=0, phase=0, firstbit=SPI.MSB, sck=Pin(config['Pin']['SD']['SCK']), mosi=Pin(config['Pin']['SD']['MOSI']), miso=Pin(config['Pin']['SD']['MISO']))
        sd = SDCard(sd_spi, Pin(config['Pin']['SD']['CS']))

        vfs = uos.VfsFat(sd)
        uos.mount(vfs, config['path']['sd_mnt'])
        return True
    except:
        return False

def sd_unmount():
    try:
        uos.umount(config['path']['sd_mnt'])
        return True
    except:
        return False