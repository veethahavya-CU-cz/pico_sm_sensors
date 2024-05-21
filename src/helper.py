import os
import logging
import json



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


def get_config():
    config = {}
    if file_exists('/config.json'):
        with open('/config.json') as f:
            config = json.load(f)
    return config

def get_logger():
    config = get_config()
    logging.basicConfig(filename=config['fpath']['log'], level=config['IO']['log']['level'], format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')
    log = logging.getLogger(__name__)
    return log