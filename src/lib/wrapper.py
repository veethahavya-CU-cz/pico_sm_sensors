# type: ignore
from usys import path
from uos import VfsFat, mount, umount
from machine import SoftI2C, Pin, SPI, ADC
from utime import sleep as pause

path.append('/lib/')
import logging as log
from helper import get_config, dir_exists
from sdcard import SDCard
from lib.rtc import DS1307



def rtc_setup():
    config = get_config()
    log.debug('Defining I2C for RTC')
    rtc_i2c = SoftI2C(scl=Pin(config['Pin']['RTC']['SCL']), sda=Pin(config['Pin']['RTC']['SDA']), freq=100_000)
    log.debug('Scanning I2C for RTC')
    rtc_check = rtc_i2c.scan()

    if not rtc_check:
        log.error('RTC not found')
        return None

    log.debug(f'RTC found at address: {rtc_check[0]}')
    return DS1307(rtc_i2c, 0x68)


def sd_mount():
    config = get_config()
    sd_root = config['path']['sd_root']
    
    if dir_exists(sd_root):
        log.warning('SD Card already mounted')
        return True

    try:
        log.debug('Defining SPI for SD Card')
        sd_spi = SPI(config['Pin']['SD']['BUS'], baudrate=1_000_000, polarity=0, phase=0, firstbit=SPI.MSB, 
                     sck=Pin(config['Pin']['SD']['SCK']), mosi=Pin(config['Pin']['SD']['MOSI']), miso=Pin(config['Pin']['SD']['MISO']))
        log.debug('Accessing SD Card via library')
        sd = SDCard(sd_spi, Pin(config['Pin']['SD']['CS']))
        log.debug('Mounting SD Card as FAT')
        mount(VfsFat(sd), sd_root)
        log.debug('SD Card mounted')
        return True
    except Exception as e:
        log.error(f'Failed to mount SD Card: {e}')
        return False


def sd_unmount():
    config = get_config()
    sd_root = config['path']['sd_root']
    
    try:
        umount(sd_root)
        return True
    except Exception as e:
        log.warning(f'Error unmounting SD Card: {e}')
        return False



def read_sm(nsensors):
    config = get_config()
    interval = config['time']['interval']['SM']['sampling']
    samples = config['samples']['per_red']['SM']

    readings = {f'SM{ns}': {'raw': [], 'mean': 0} for ns in range(1, nsensors + 1)}

    for ns in range(1, nsensors + 1):
        sm_adc = ADC(config['ADC'][f'SM{ns}'])
        readings[f'SM{ns}']['raw'] = [sm_adc.read_u16() for _ in range(samples)]
        readings[f'SM{ns}']['mean'] = sum(readings[f'SM{ns}']['raw']) / samples
        pause(interval)

    return readings


# TODO: Implement read_temp
def read_temp():
    pass

# FIXME: something is wrong
def read_internal_temp():
    config = get_config()
    interval = config['time']['interval']['INTERNAL_TEMP']['sampling']
    samples = config['samples']['per_red']['INTERNAL_TEMP']

    try:
        temp_adc = ADC(ADC.CORE_TEMP)
    except Exception:
        temp_adc = ADC(config['ADC'].get('CORE_TEMP'))
        if not temp_adc:
            log.critical('Temperature sensor not found')
            return None

    readings = [temp_adc.read_u16() for _ in range(samples)]
    pause(interval)

    voltage = sum(readings) / samples
    temperature = 27 - (voltage * (3.3 / 65536) - 0.706) / 0.001721

    return temperature

# FIXME: something is wrong (tip throw out 1-3 readings)
def read_battery():
    config = get_config()
    interval = config['time']['interval']['VSYS']['sampling']
    samples = config['samples']['per_red']['VSYS']
    
    batt_adc = ADC(config['ADC']['VSYS'])
    readings = [batt_adc.read_u16() for _ in range(samples)]
    pause(interval)

    avg_reading = sum(readings) / samples
    battery_voltage = avg_reading * (3 * 3.3 / 65536)
    battery_percentage = (battery_voltage - 3.2) / (4.2 - 3.3) * 100

    return battery_voltage, battery_percentage