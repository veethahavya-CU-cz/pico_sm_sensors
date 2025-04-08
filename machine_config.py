CONFIG = {
    # Datetime is updated automatically from system if running flash_station.[sh|bat|ps1]; ID and LOC are expected as arguments to the script
    # Station Identification
    'ID': None,
    'LOC': None,
    'NOTES': None,
    # RTC Date and Time updation [YYYY, MM, DD, HH, MM, SS, DoW, DoY]
    'datetime': None,
    # Time, Period, and Frequency definitions
    'time': {
        # Time to wake up before next record time (s)
        'wake_haste': 5,
        # Pause (s) before putting machine to sleep
        'sleep_buffer_pause': 0.5,
        ## Sampling and Logging intervals (s)
        'interval': {
            'SM':       {'logging': 15 * 60, 'sampling': 0.1},
            'DHT11':    {'logging': None, 'sampling': None},
            'ITEMP':    {'logging': 30 * 60, 'sampling': 0.1},
            'VSYS':     {'logging': 30 * 60, 'sampling': 0.1},
        },
    },
    # Number of samples per reading
    'samples': {'per_red': {'SM': 10, 'DHT11': 3, 'ITEMP': 7, 'VSYS': 7}},
    # Number of sensors
    'nsensors': {'SM': 3, 'DHT11': 0},
    # Pin definitions
    'Pin': {
        ## GPIO Pins
        'led': 25,
        'status_led': {'red': 14, 'green': 13, 'blue': 12},
        'logger_switch': 15,
        'UART': {'BUS': 0, 'TX': 0, 'RX': 1},
        'RTC': {'BUS': 1, 'SCL': 7, 'SDA': 6},
        'SD': {'BUS': 0, 'SCK': 2, 'MOSI': 3, 'MISO': 4, 'CS': 5},
        'DHT11': 9,
    },
    'BAUD': {'UART': 9_600, 'SPI': 1_000_000, 'I2C': 80_000},
    ## ADC Channels
    'ADC': {'SM1': 0, 'SM2': 1, 'SM3': 2, 'VSYS': 3, 'temperature': 4},
    ## Depth SM of sensors
    'depth': {'SM1': 15, 'SM2': 40, 'SM3': 60},
    # Formats
    'format': {'time': '%Y-%m-%d %H:%M:%S'},
    # I/O Configuration
    'IO': {
        ## Record Internal Temperature
        'ITEMP': True,
        ## Record Battery Voltage/Percentage
        'BATT': True,
        ## Logging Configuration
        #TODO: Add status_LED opts
        'log': {'file': '/sd/sys.log', 'level': 'DEBUG', 'UART': True},  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    },
    # Path Configurations
    'path': {
        'src': '/',
        'lib': '/lib/',
        'usr-lib': '/usr/lib/',
        'sd_root': '/sd',
        'out': {'root': '/sd', 'records': '/sd/records', 'config': '/sd/.config', 'cache': '/sd/.cache', 'data': '/sd/data'},
    },
    # File Configurations
    'files': {
        'src': ['boot.py', 'main.py'],
        'lib': ['upysh.mpy', 'os/__init__.mpy', 'os/path.mpy', 'datetime.mpy', 'dht.mpy', 'ds1307/__init__.py', 'ds1307/ds1307.py', 'sdcard.mpy'],
        'usr-lib': ['picostation_logging.py', 'picostation_helper.py', 'picostation_wrapper.py'],
    },
    'fpath': {
        'config': '/config.json',
        'sm': '/sd/records/sm',
        'sm_raw': '/sd/data/sm',
        'meteo': '/sd/records/meteo',
        'itemp': '/sd/data/itemp',
        'battery': '/sd/data/battery',
    },
}
