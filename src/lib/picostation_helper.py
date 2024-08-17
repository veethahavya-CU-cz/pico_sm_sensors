from usys import path as sys_path
from utime import localtime, mktime
from ujson import load as load_json

from os import path
from datetime import datetime, timedelta

sys_path.append('/usr/lib')
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
            config = load_json(f)
        return config
    else:
        try:
            with open('/config.json') as f:
                config = load_json(f)
            return config
        except:
            log.error(f"@helper.py/get_config: Config file not found at {filepath}")
            raise ValueError("Config file not found")


def get_next_record_time(interval):
    # Get current time as a datetime object
    now = datetime(*localtime()[:-2])
    
    # Calculate the current minute and second
    current_minutes = now.minute
    current_seconds = now.second
    
    # Determine the next interval time in minutes
    next_minutes = (current_minutes // interval + 1) * interval
    
    # If next_minutes overflows to the next hour, adjust accordingly
    if next_minutes >= 60:
        next_minutes -= 60
        now = now.replace(hour=now.hour + 1)
    
    # Set the next time, keeping the hour, setting minutes and zeroing seconds and microseconds
    next_time = now.replace(minute=next_minutes, second=0, microsecond=0)
    
    # Convert to tuple (timestamp, ISO 8601 string)
    return mktime(next_time.timetuple()), next_time.isoformat()


def prep_next_ts():
    config = get_config(filepath='/sd/config.json')
    log.info('Preparing for next timestep')

    recs = []
    interval_dht = config['time']['interval']['DHT11']['logging']
    next_dht_record_time, next_dht_record_timestamp = get_next_record_time(interval_dht) if interval_dht else None, None
    if next_dht_record_time:
        log.info(f"Next DHT11 record time: ({next_dht_record_timestamp})")

    next_sm_record_time, next_sm_record_timestamp = get_next_record_time(config['time']['interval']['SM']['logging'])
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
