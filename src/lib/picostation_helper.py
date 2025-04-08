from usys import path as sys_path
from utime import localtime, mktime
from ujson import load as load_json

from os import path
from datetime import datetime, timedelta

sys_path.insert(0, '/usr/lib')
import picostation_logging as log


def median(data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        return sorted_data[mid]


def mean(data):
    return sum(data) / len(data)


def get_config(filepath='/config.json'):
    if path.exists(filepath):
        with open(filepath) as f:
            CONFIG = load_json(f)
        return CONFIG
    else:
        try:
            try:
                CONFIG = get_config()
                return CONFIG
            except:
                from machine_config import CONFIG
                return CONFIG
        except:
            log.error(f"@helper/get_config: Config file not found at {filepath}")
            raise ValueError("Config file not found")


def get_next_record_time(interval_s):
    # HACK: Works only for hourly and sub-hourly intervals
    now = datetime(*localtime()[:-2])

    total_seconds_this_hr = (now.minute * 60) + now.second
    intervals_passed_in_hr = total_seconds_this_hr // interval_s
    next_interval_seconds_in_hr = (intervals_passed_in_hr + 1) * interval_s
    seconds_to_next_interval = next_interval_seconds_in_hr - total_seconds_this_hr

    next_record_time_dt = now + timedelta(seconds=seconds_to_next_interval)

    return (
        mktime(
            (
                next_record_time_dt.year,
                next_record_time_dt.month,
                next_record_time_dt.day,
                next_record_time_dt.hour,
                next_record_time_dt.minute,
                next_record_time_dt.second,
            )
            + localtime()[-2:]
        ),
        next_record_time_dt.isoformat(),
    )


def prep_next_ts():
    CONFIG = get_config()
    log.info('Preparing for next timestep')

    recs = []

    next_sm_record_time, next_sm_record_timestamp = get_next_record_time(CONFIG['time']['interval']['SM']['logging'])
    log.debug(f"Next SM record time: ({next_sm_record_timestamp})")

    interval_dht = CONFIG['time']['interval']['DHT11']['logging']
    next_dht_record_time, next_dht_record_timestamp = get_next_record_time(interval_dht) if interval_dht else (None, None)
    if next_dht_record_time:
        log.debug(f"Next DHT11 record time: ({next_dht_record_timestamp})")

    next_itemp_record_time, next_itemp_record_timestamp = get_next_record_time(CONFIG['time']['interval']['ITEMP']['logging'])
    log.debug(f"Next ITEMP record time: ({next_itemp_record_timestamp})")

    next_batt_record_time, next_batt_record_timestamp = get_next_record_time(CONFIG['time']['interval']['VSYS']['logging'])
    log.debug(f"Next BATT record time: ({next_batt_record_timestamp})")

    next_record_times = [next_sm_record_time, next_dht_record_time, next_itemp_record_time, next_batt_record_time]
    next_dht_record_timestamps = [
        next_sm_record_timestamp,
        next_dht_record_timestamp,
        next_itemp_record_timestamp,
        next_batt_record_timestamp,
    ]
    next_record_time = min(filter(lambda x: x is not None, next_record_times))
    next_record_timestamp = next_dht_record_timestamps[next_record_times.index(next_record_time)]

    recs.append('SM') if next_record_time == next_sm_record_time else None
    recs.append('DHT11') if next_record_time == next_dht_record_time else None
    recs.append('ITEMP') if next_record_time == next_itemp_record_time else None
    recs.append('BATT') if next_record_time == next_batt_record_time else None

    cache_path = CONFIG['path']['out']['cache']
    with open(f"{cache_path}/recs", 'w') as f:
        f.write('\n'.join(recs))
    with open(f"{cache_path}/rec_time", 'w') as f:
        f.write(f"{next_record_time}\n{next_record_timestamp}\n")
    log.debug(f"Next record time ({next_record_time}; {next_record_timestamp}) saved to cache file.")

    return next_record_time, next_record_timestamp
