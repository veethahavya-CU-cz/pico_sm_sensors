# type: ignore
import os, sys
import time

import json

sys.path.append('./lib/')
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
    try:
        with open(src, 'rb') as f:
            with open(dst, 'wb') as g:
                g.write(f.read())
    except:
        try:
            with open(src, 'r') as f:
                with open(dst, 'w') as g:
                    g.write(f.read())
        except:
            pass

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



def strf_time(time, mode='time_tuple'):
    if mode == 'time_tuple':
        return f"{time[0]:04d}-{time[1]:02d}-{time[2]:02d} {time[3]:02d}:{time[4]:02d}:{time[5]:02d}"
    
    elif mode == 'unix_epoch':
        SECONDS_IN_MINUTE = 60
        SECONDS_IN_HOUR = 3600
        SECONDS_IN_DAY = 86400
        DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        epoch = time
        year = 1970
        while True:
            days_in_year = 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
            if epoch < days_in_year * SECONDS_IN_DAY:
                break
            epoch -= days_in_year * SECONDS_IN_DAY
            year += 1

        month = 0
        while True:
            days_in_this_month = DAYS_IN_MONTH[month]
            if month == 1 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
                days_in_this_month += 1
            if epoch < days_in_this_month * SECONDS_IN_DAY:
                break
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
        log.error('@helper.py/strf_time: Invalid mode')
        raise ValueError('Invalid mode')


def get_next_record_time(current_time, interval, mode='unix_epoch'):
    def is_leap_year(year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def days_in_month(year, month):
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            return 29 if is_leap_year(year) else 28
        return 0
    
    if mode == 'time_tuple':
        year, month, day, hour, minute, second, _, _ = current_time

        intervals_passed = minute // interval
        next_interval_minute = (intervals_passed + 1) * interval

        if next_interval_minute >= 60:
            next_interval_minute -= 60
            hour += 1
            if hour >= 24:
                hour = 0
                day += 1
                if day > days_in_month(year, month):
                    day = 1
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
        
        return (year, month, day, hour, next_interval_minute, 0)

    elif mode == 'unix_epoch':
        interval_seconds = interval * 60
        next_epoch = ((current_time + interval_seconds - 1) // interval_seconds) * interval_seconds
        return next_epoch
    else:
        raise ValueError('Invalid mode')


def prep_next_ts():
    config = get_config()
    log.info('Preparing for next timestep')

    recs = []
    if not config['time']['interval']['DHT11']['logging'] == None:
        next_dht_record_time = get_next_record_time(time.time(), config['time']['interval']['DHT11']['logging'], mode='unix_epoch')
        next_dht_record_timestamp = strf_time(get_next_record_time(time.localtime(), config['time']['interval']['DHT11']['logging']//60, 'time_tuple'))
        log.info(f"Next DHT11 record time: ({next_dht_record_timestamp})")
    else:
        next_dht_record_time = None

    next_sm_record_time = get_next_record_time(time.time(), config['time']['interval']['SM']['logging'], mode='unix_epoch')
    next_sm_record_timestamp = strf_time(get_next_record_time(time.localtime(), config['time']['interval']['SM']['logging']//60, 'time_tuple'))
    log.info(f"Next SM record time: ({next_sm_record_timestamp})")

    if not next_dht_record_time == None:
        if next_sm_record_time == next_dht_record_time:
            next_record_time = next_sm_record_time
            next_record_timestamp = next_sm_record_timestamp
            recs.append('SM')
            recs.append('DHT11')
        else:
            next_record_time = min(next_dht_record_time, next_sm_record_time)
            next_record_timestamp = next_dht_record_timestamp if next_record_time == next_dht_record_time else next_sm_record_timestamp
            recs.append('SM' if next_record_time == next_sm_record_time else 'DHT11')
    else:
        next_record_time = next_sm_record_time
        next_record_timestamp = next_sm_record_timestamp
        recs.append('SM')
    log.info(f"Next record time: ({next_record_timestamp})")

    recs.append('ITEMP')
    recs.append('BATT')
    with open(config['path']['out']['cache'] + '/recs', 'w') as f:
        f.write('\n'.join(recs))
    log.debug("Next record time saved to cache file.")
    with open(config['path']['out']['cache'] + '/rec_time', 'w') as f:
        f.write(str(next_record_time) + '\n')
        f.write(str(next_record_timestamp) + '\n')
    log.debug("Next record time saved to cache file.")

    return next_record_time, next_record_timestamp