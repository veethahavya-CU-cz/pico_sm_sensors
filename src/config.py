sd_root = '/sd' # not modifiable

CONFIG = {
    # Station Identification
    'ID': 4,
    'LOC': 'station4',
    'NOTES': 'marker: D',
    # RTC Date and Time updation [YYYY, MM, DD, HH, MM, SS, DOW]
    'datetime': [2024, 7, 17, 3, 19, 0, 1],
    # Time, Period, and Frequency definitions
    'time': {
        'wake_haste': 7,
        ## Sampling and Logging intervals
        'interval': {
            'SM': {'logging': 15 * 60, 'sampling': 0.1},
            'DHT11': {'logging': None, 'sampling': None},
            'INTERNAL_TEMP': {'sampling': 0.1},
            'VSYS': {'sampling': 0.1},
            'UART_BAUD': 115200
        }
    },
    # Number of samples per reading
    'samples': {
        'per_red': {'SM': 10, 'DHT11': 5, 'INTERNAL_TEMP': 7, 'VSYS': 7}
    },
    # Number of sensors
    'nsensors': {
        'SM': 3, 'DHT11': 0
    },
    # Pin definitions
    'Pin': {
        ## GPIO Pins
        'led': 25,
        'UART': {'BUS': 0, 'TX': 0, 'RX': 1},
        'RTC': {'SCL': 7, 'SDA': 6},
        'SD': {'BUS': 0, 'SCK': 2, 'MOSI': 3, 'MISO': 4, 'CS': 5},
        'DHT11': 20
    },
    ## ADC Channels
    'ADC': {
        'SM1': 0, 'SM2': 1, 'SM3': 2, 'VSYS': 3, 'temperature': 4
    },
    ## Depth SM of sensors
    'depth': {
        'SM1': 15, 'SM2': 40, 'SM3': 60
    },
    # Formats
    'format': {
        'time': '%Y-%m-%d %H:%M:%S'
    },
    # I/O Configuration
    'IO': {
        ## Record Internal Temperature
        'ITEMP': True,
        ## Record Battery Voltage/Percentage
        'BATT': True,
        ## Logging Configuration
        'log': {
            'file': 'sys.log',
            'level': 'DEBUG',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            'UART': True
        }
    },
    # Path Configurations
    'path': {
        'src': '/',
        'lib': '/lib/',
        'sd_root': f'{sd_root}',
        'out': {
            'root': f'{sd_root}',
            'records': f'{sd_root}/records',
            'config': f'{sd_root}/.config',
            'cache': f'{sd_root}/.cache',
            'data': f'{sd_root}/data'
        }
    },
    # File Configurations
    'files': {
        'src': ['boot.py', 'main.py'],
        'lib': ['logging.py', 'helper.py', 'wrapper.py', 'ds1307.py', 'sdcard.py', 'dht11.py']
    },
    'fpath': {
        'config': '/config.json',
        'log': f'{sd_root}/sys.log',
        'sm': f'{sd_root}/records/sm',
        'sm_raw': f'{sd_root}/records/sm',
        'meteo': f'{sd_root}/records/meteo',
        'itemp': f'{sd_root}/data/itemp',
        'battery': f'{sd_root}/data/battery'
    }
}