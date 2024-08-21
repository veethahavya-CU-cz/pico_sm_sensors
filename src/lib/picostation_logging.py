from uos import remove
from utime import localtime
from utime import sleep as pause
from ujson import load as load_json
from machine import UART

from os import path


# Load configuration
config_path = '/config.json'
default_log_path = '/stray.log'
levels = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}

if path.exists(config_path):
    with open(config_path) as config_file:
        CONFIG = load_json(config_file)
    log_path = CONFIG['IO']['log']['file']
    log_level = CONFIG['IO']['log']['level']
    if CONFIG['IO']['log']['UART']:
        try:
            uart_obj = UART(
                CONFIG['Pin']['UART']['BUS'],
                baudrate=CONFIG['BAUD']['UART'],
                tx=CONFIG['Pin']['UART']['TX'],
                rx=CONFIG['Pin']['UART']['RX'],
            )
        except KeyError:
            uart_obj = None
else:
    uart_obj = None
    with open('/LOGGER_FILE_WARNING', 'w') as warning_file:
        warning_file.write("Config file not found while logging. It might be fixed later on. Check '/sd/sys.log' for more info.")
    log_path = default_log_path
    log_level = 'DEBUG'


def get_str_time():
    t = localtime()
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"


def init(file='/sys.log', lvl='INFO', rewrite=False, uart_out=None):
    global log_path, log_level, uart_obj
    log_path, log_level = file, lvl
    if rewrite:
        open(log_path, 'w').close()
    if not uart_out == None:
        uart_obj = UART(uart_out[0], baudrate=uart_out[1], tx=uart_out[2], rx=uart_out[3])
    else:
        uart_obj = None


def move_logfile(new_log_path, rewrite=False):
    global log_path
    if path.exists(log_path):
        with open(log_path, 'r') as old_log_file:
            records = old_log_file.read()
        remove(log_path)
    else:
        records = ""

    if path.exists('/LOGGER_FILE_WARNING'):
        remove('/LOGGER_FILE_WARNING')

    with open(new_log_path, 'w' if rewrite else 'a') as new_log_file:
        if not rewrite:
            new_log_file.write("\n...\n...\n")
        new_log_file.write(records)

    log_path = new_log_path


def update_level(new_level):
    global log_level
    log_level = new_level


def write_msg(slevel, msg):
    if levels[log_level] <= levels[slevel]:
        try:
            with open(log_path, 'a') as log_file:
                log_file.write(f"[{slevel}] {get_str_time()} {msg}\n")
                if uart_obj:
                    uart_obj.write(f"[{slevel}] {get_str_time()} {msg}")
                    pause(0.1)
        except:
            with open(default_log_path, 'a') as stray_log_file:
                stray_log_file.write(f"[{slevel}] {get_str_time()} {msg}\n")
                if uart_obj:
                    uart_obj.write(f"[{slevel}] {get_str_time()} {msg}")
                    pause(0.1)


def debug(msg):
    write_msg('DEBUG', msg)


def info(msg):
    write_msg('INFO', msg)


def warning(msg):
    write_msg('WARNING', msg)


def error(msg):
    write_msg('ERROR', msg)


def critical(msg):
    write_msg('CRITICAL', msg)
