# type: ignore
import sys, os
import json

sys.path.append('/lib')
import logging as log


def dir_exists(path):
    try:
        return os.stat(path)[0] & 0x4000 != 0
    except OSError:
        return False

def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

def cp(src, dst):
    with open(src, 'rb') as f:
        with open(dst, 'wb') as g:
            g.write(f.read())

def mv(src, dst):
    os.rename(src, dst)


def get_config():
    config = {}
    if file_exists('/config.json'):
        with open('/config.json') as f:
            config = json.load(f)
        return config
    else:
        log.error('Config file not found')
        raise ValueError('Config file not found')


def strf_time(time, mode='clock.datetime'):
    if mode in ['time.localtime', 'clock.datetime']:
        return f"{time[0]:04d}-{time[1]:02d}-{time[2]:02d} {time[3]:02d}:{time[4]:02d}:{time[5]:02d}"
    else:
        log.error('@helper.py/strf_time: Invalid mode')
        raise ValueError('Invalid mode')