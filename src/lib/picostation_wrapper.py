from usys import path as sys_path
from uos import VfsFat, mount, umount
from machine import Pin, I2C, SPI, ADC, PWM
from utime import sleep as pause

from os import path
from sdcard import SDCard
from ds1307 import DS1307
from dht import DHT11

sys_path.insert(0, '/usr/lib')
import picostation_logging as log
from picostation_helper import get_config, mean, median


def rtc_setup():
    CONFIG = get_config()
    log.debug("Defining I2C for RTC")
    rtc_i2c = I2C(id=CONFIG['Pin']['RTC']['BUS'], scl=Pin(CONFIG['Pin']['RTC']['SCL']), sda=Pin(CONFIG['Pin']['RTC']['SDA']), freq=CONFIG['BAUD']['I2C'])
    log.debug("Scanning I2C for RTC")
    rtc_check = rtc_i2c.scan()

    if not rtc_check:
        status_led('flash/error_rtc')
        log.error("@wrapper/rtc_setup: RTC not found")
        return None

    log.debug(f"RTC found at address: {rtc_check[0]}")
    return DS1307(i2c=rtc_i2c)


def sd_mount(format=False):
    CONFIG = get_config()
    sd_root = '/sd'

    if path.exists(sd_root):
        log.warning("@wrapper/sd_mount: SD Card already mounted")
        return True

    try:
        log.debug("Defining SPI for SD Card")
        sd_spi = SPI(
            id=CONFIG['Pin']['SD']['BUS'],
            baudrate=CONFIG['BAUD']['SPI'],
            sck=Pin(CONFIG['Pin']['SD']['SCK']),
            mosi=Pin(CONFIG['Pin']['SD']['MOSI']),
            miso=Pin(CONFIG['Pin']['SD']['MISO']),
        )
        log.debug("Creating SD Card object")
        sd = SDCard(sd_spi, Pin(CONFIG['Pin']['SD']['CS']))
        log.debug("Mounting SD Card as FAT")
        try:
            mount(VfsFat(sd), sd_root)
            log.debug("SD Card mounted")
        except OSError:
            log.error("@wrapper/sd_mount: Failed to mount SD Card")
            if format:
                log.info("Error mounting SDcard. Formatting SD Card")
                VfsFat.mkfs(sd)
                log.debug("SD Card formatted successfully. Mounting SD Card as FAT.")
                mount(VfsFat(sd), sd_root)
                log.debug("SD Card mounted")
        return True
    except Exception as e:
        status_led('flash/error_sd')
        log.error(f"@wrapper/sd_mount: Failed to mount SD Card: {e}")
        return False


def sd_unmount():
    sd_root = '/sd'

    try:
        umount(sd_root)
        return True
    except Exception as e:
        log.warning(f"@wrapper/sd_unmount: Error unmounting SD Card: {e}")
        return False


def status_led(state, var=None, flash_count=3, flash_in=0.33, flash_out=0.1, pause_after=0.1):
    CONFIG = get_config()

    def led(color_name, freq=1000):
        r = PWM(Pin(CONFIG['Pin']['status_led']['red']), freq=freq)
        g = PWM(Pin(CONFIG['Pin']['status_led']['green']), freq=freq)
        b = PWM(Pin(CONFIG['Pin']['status_led']['blue']), freq=freq)

        colors = {
            'red': (65535, 0, 0),
            'green': (0, 21845, 0),
            'blue': (0, 0, 32767),
            'cyan': (0, 32767, 32767),
            'yellow': (52428, 13107, 0),
            'magenta': (65535, 0, 32767),
            'white': (65535, 32767, 32767),
            'orange': (65535, 6553, 0),
            'pink': (65535, 8192, 13107),
            'lightblue': (32767, 32767, 65535),
            'lightgreen': (32767, 49150, 3276),
            'off': (0, 0, 0),
        }
        if color_name in colors:
            r.duty_u16(colors[color_name][0])
            g.duty_u16(colors[color_name][1])
            b.duty_u16(colors[color_name][2])
        else:
            log.error(f"@led: Error: Invalid color name '{color_name}'")

    if state == 'busy':
        led('yellow')
    elif state == 'error':
        led('red')
    elif state == 'success':
        led('green')
    elif state == 'idle':
        led('white')
    elif state == 'measuring':
        if var == 'sm':
            led('cyan')
        elif var == 'dht11':
            led('pink')
        elif var == 'ITEMP':
            led('magenta')
        elif var == 'battery':
            led('lightblue')
        else:
            led('white')
    elif state == 'off':
        led('off')
    elif state == 'flash/busy':
        for _ in range(flash_count):
            led('yellow')
            pause(flash_in)
            led('off')
            pause(0.25)
    elif state == 'flash/error':
        for _ in range(flash_count):
            led('red')
            pause(flash_in)
            led('off')
            pause(flash_out)
    elif state == 'flash/success':
        for _ in range(flash_count):
            led('green')
            pause(flash_in)
            led('off')
            pause(flash_out)
    elif state == 'flash/idle':
        for _ in range(flash_count):
            led('white')
            pause(flash_in)
            led('off')
            pause(flash_out)
    elif state == 'flash/critical':
        for _ in range(flash_count):
            led('red')
            pause(flash_in)
            led('orange')
            pause(flash_out)
    elif state == 'flash/measuring':
        for _ in range(flash_count):
            led('cyan')
            pause(flash_in)
            led('off')
            pause(flash_out)
    elif state == 'flash/busy_measuring':
        if var.lower() == 'sm':
            for _ in range(flash_count):
                led('yellow')
                pause(flash_in)
                led('cyan')
                pause(flash_out)
            led('off')
        elif var.lower() == 'dht11':
            for _ in range(flash_count):
                led('yellow')
                pause(flash_in)
                led('pink')
                pause(flash_out)
            led('off')
        elif var.lower() == 'itemp':
            for _ in range(flash_count):
                led('yellow')
                pause(flash_in)
                led('magenta')
                pause(flash_out)
            led('off')
        elif var.lower() == 'batt':
            for _ in range(flash_count):
                led('yellow')
                pause(flash_in)
                led('lightblue')
                pause(flash_out)
            led('off')
        else:
            for _ in range(flash_count):
                led('yellow')
                pause(flash_in)
                led('white')
                pause(flash_out)
            led('off')
    elif state == 'flash/error_measuring':
        for _ in range(flash_count):
            led('red')
            pause(flash_in)
            led('cyan')
            pause(flash_out)
        led('off')
    elif state == 'flash/success_measuring':
        for _ in range(flash_count):
            led('green')
            pause(flash_in)
            led('cyan')
            pause(flash_out)
        led('off')
    elif state == 'flash/error_sd':
        for _ in range(flash_count):
            led('red')
            pause(flash_in)
            led('pink')
            pause(flash_out)
        led('off')
    elif state == 'flash/error_rtc':
        for _ in range(flash_count):
            led('red')
            pause(flash_in)
            led('blue')
            pause(flash_out)
        led('off')
    else:
        log.error(f"@status_led: Error: Invalid state '{state}'")
    pause(pause_after)


def read_sm(nsensors):
    CONFIG = get_config()
    interval = CONFIG['time']['interval']['SM']['sampling']
    samples = CONFIG['samples']['per_red']['SM']

    readings = {f'SM{ns}': {'raw': [], 'mean': 0} for ns in range(1, nsensors + 1)}

    for ns in range(1, nsensors + 1):
        sm_adc = ADC(CONFIG['ADC'][f'SM{ns}'])
        readings[f'SM{ns}']['raw'] = [sm_adc.read_u16() for _ in range(samples)]
        readings[f'SM{ns}']['mean'] = sum(readings[f'SM{ns}']['raw']) / samples
        pause(interval)

    return readings


def read_dht11():
    CONFIG = get_config()
    sensor = DHT11(Pin(CONFIG['Pin']['DHT11'], Pin.OUT, Pin.PULL_DOWN))
    n = 0
    while n < 5:
        try:
            sensor.measure()
            pause(0.5)
            temp = sensor.temperature()
            hum = sensor.humidity()
            return temp, hum
        except Exception as e:
            n += 1
            log.debug(f"@wrapper/read_dht11: Failed to read DHT11 [attempt {n}]: {e}")
            pause(0.5)
    log.error("@wrapper/read_dht11: Failed to read DHT11")


def read_internal_temp():
    CONFIG = get_config()
    interval = CONFIG['time']['interval']['ITEMP']['sampling']
    samples = CONFIG['samples']['per_red']['ITEMP']

    try:
        temp_adc = ADC(ADC.CORE_TEMP)
    except Exception:
        temp_adc = ADC(CONFIG['ADC'].get('CORE_TEMP'))
        if not temp_adc:
            log.critical("@wrapper/read_internal_temp: Temperature sensor not found")
            return None

    readings = [temp_adc.read_u16() for _ in range(samples)]
    pause(interval)

    reading = mean(readings)
    temperature = 27 - (reading * (3.3 / 65536) - 0.706) / 0.001721

    return temperature


def read_battery():
    CONFIG = get_config()
    interval = CONFIG['time']['interval']['VSYS']['sampling']
    samples = CONFIG['samples']['per_red']['VSYS']

    batt_adc = ADC(CONFIG['ADC']['VSYS'])
    readings = []
    for _ in range(samples):
        readings.append(batt_adc.read_u16())
        pause(interval)

    med_readings = median(readings)
    battery_voltage = med_readings * ((3 * 3 * 3.3) / (65536 * 0.79))
    battery_percentage = (battery_voltage - 3.2) / (4.2 - 3.3) * 100

    return battery_voltage, battery_percentage
