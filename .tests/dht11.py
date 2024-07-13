from machine import Pin, I2C
from utime import time, sleep
from dht11 import DHT11, InvalidChecksum
import picosleep

while True:
    time.sleep(1)
    pin = Pin(0, Pin.OUT, Pin.PULL_DOWN)
    sensor = DHT11(pin)
    t  = (sensor.temperature)
    h = (sensor.humidity)
    print("Temperature: {}".format(sensor.temperature))
    print("Humidity: {}".format(sensor.humidity))
    sleep(2)
