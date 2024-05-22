# type: ignore
import sys, os
import json
import time


def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

config = {}
if file_exists('/config.json'):
    with open('/config.json') as f:
        config = json.load(f)
else:
    with open('/ERR', 'w') as f:
        f.write('Config file not found!')
    raise ValueError('Config file not found')

fpath = config['fpath']['log']
level = config['IO']['log']['level']

levels = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}


def strf_time(time, mode='clock.datetime'):
    if mode in ['time.localtime', 'clock.datetime']:
        return f"{time[0]:04d}-{time[1]:02d}-{time[2]:02d} {time[3]:02d}:{time[4]:02d}:{time[5]:02d}"

def init(file='/sys.log', lvl='INFO', rewrite=False):
    global fpath
    global level
    fpath = file
    level = lvl
    if rewrite:
        open(fpath, 'w').close()


def move(new_fpath, rewrite=False):
    global fpath

    with open(fpath, 'r') as f:
        records = f.read()
    os.remove(fpath)

    if rewrite:
        with open(new_fpath, 'w') as f:
            f.write(records)
    else:
        with open(new_fpath, 'a') as f:
            f.write("\n...")
            f.write("\n")
            f.write("...")
            f.write(records)

    fpath = new_fpath


def update_level(new_level):
    global level
    level = new_level


def debug(msg):
    try:
        if levels[level] <= levels['DEBUG']:
            with open(fpath, 'a') as f:
                f.write("[DEBUG] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")
    except:
        with open('/stray.log', 'a') as f:
            f.write("[DEBUG] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")

def info(msg):
    try:
        if levels[level] <= levels['INFO']:
            with open(fpath, 'a') as f:
                f.write("[INFO] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")
    except:
        with open('/stray.log', 'a') as f:
            f.write("[INFO] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")

def warning(msg):
    try:
        if levels[level] <= levels['WARNING']:
            with open(fpath, 'a') as f:
                f.write("[WARNING] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")
    except:
        with open('/stray.log', 'a') as f:
            f.write("[WARNING] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")

def error(msg):
    try:
        if levels[level] <= levels['ERROR']:
            with open(fpath, 'a') as f:
                f.write("[ERROR] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")
    except:
        with open('/stray.log', 'a') as f:
            f.write("[ERROR] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")

def critical(msg):
    try:
        if levels[level] <= levels['CRITICAL']:
            with open(fpath, 'a') as f:
                f.write("[CRITICAL] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")
    except:
        with open('/stray.log', 'a') as f:
            f.write("[CRITICAL] " + strf_time(time.localtime(), 'time.localtime') + " " + msg + "\n")