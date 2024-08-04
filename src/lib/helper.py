# type: ignore
from usys import path
from uos import stat, rename
from utime import time
from micropython import const
from array import array
from ujson import load as load_json

path.append('./lib/')
import logging as log



def dir_exists(path):
    try:
        return stat(path)[0] & 0x4000 != 0
    except OSError:
        return False

def file_exists(filename):
    try:
        stat(filename)
        return True
    except OSError:
        return False

def cp(src, dst):
    try:
        with open(src, 'rb') as src_file, open(dst, 'wb') as dst_file:
            dst_file.write(src_file.read())
    except:
        try:
            with open(src, 'r') as src_file, open(dst, 'w') as dst_file:
                dst_file.write(src_file.read())
        except Exception as e:
            log.error(f"@helper.py/cp: {e}")
            raise

def mv(src, dst):
    rename(src, dst)


def get_config():
    config = {}
    if file_exists('/config.json'):
        with open('/config.json') as f:
            config = load_json(f)
        return config
    else:
        log.error("@helper.py/get_config: Config file not found")
        raise ValueError("Config file not found")


def strf_time(time, mode):
    if mode == 'time.localtime':
        return f"{time[0]:04d}-{time[1]:02d}-{time[2]:02d} {time[3]:02d}:{time[4]:02d}:{time[5]:02d}"
    elif mode == 'time.time':
        SECONDS_IN_MINUTE = const(60)
        SECONDS_IN_HOUR = const(3600)
        SECONDS_IN_DAY = const(86400)
        DAYS_IN_MONTH = array('I', [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

        epoch = time
        year = 1970

        while epoch >= (days_in_year := 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365) * SECONDS_IN_DAY:
            epoch -= days_in_year * SECONDS_IN_DAY
            year += 1

        month = 0
        while epoch >= (days_in_this_month := DAYS_IN_MONTH[month] + (1 if month == 1 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 0)) * SECONDS_IN_DAY:
            epoch -= days_in_this_month * SECONDS_IN_DAY
            month += 1

        day = epoch // SECONDS_IN_DAY
        epoch %= SECONDS_IN_DAY
        hour = epoch // SECONDS_IN_HOUR
        epoch %= SECONDS_IN_HOUR
        minute = epoch // SECONDS_IN_MINUTE
        second = epoch % SECONDS_IN_MINUTE

        return f"{year:04}-{month + 1:02}-{day + 1:02} {hour:02}:{minute:02}:{second:02}"
    else:
        log.error("@helper.py/strf_time: Invalid mode")
        raise ValueError("Invalid mode")

def get_next_record_time(current_time, interval):
    return ((current_time // interval) + 1) * interval


def prep_next_ts():
    config = get_config()
    log.info('Preparing for next timestep')

    recs = []
    current_time = time()
    interval_dht = config['time']['interval'].get('DHT11', {}).get('logging')
    next_dht_record_time = get_next_record_time(current_time, interval_dht) if interval_dht else None

    if next_dht_record_time:
        next_dht_record_timestamp = strf_time(next_dht_record_time, 'time.time')
        log.info(f"Next DHT11 record time: ({next_dht_record_timestamp})")
    
    next_sm_record_time = get_next_record_time(current_time, config['time']['interval']['SM']['logging'])
    next_sm_record_timestamp = strf_time(next_sm_record_time, 'time.time')
    log.info(f"Next SM record time: ({next_sm_record_timestamp})")

    if next_dht_record_time and next_sm_record_time:
        next_record_time = min(next_dht_record_time, next_sm_record_time)
        next_record_timestamp = next_dht_record_timestamp if next_record_time == next_dht_record_time else next_sm_record_timestamp
        recs.extend(['SM', 'DHT11'] if next_record_time == next_sm_record_time else ['DHT11', 'SM'])
    else:
        next_record_time = next_sm_record_time
        next_record_timestamp = next_sm_record_timestamp
        recs.append('SM')

    recs.extend(['ITEMP', 'BATT'])

    cache_path = config['path']['out']['cache']
    with open(f"{cache_path}/recs", 'w') as f:
        f.write('\n'.join(recs))
    with open(f"{cache_path}/rec_time", 'w') as f:
        f.write(f"{next_record_time}\n{next_record_timestamp}\n")
    log.debug("Next record time saved to cache file.")

    return next_record_time, next_record_timestamp