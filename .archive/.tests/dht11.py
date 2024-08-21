from machine import Pin
from utime import sleep
from dht import DHT11

while True:
    sleep(1)
    pin = Pin(9, Pin.OUT, Pin.PULL_DOWN)
    sensor = DHT11(pin)
    sensor.measure()
    sleep(0.5)
    t  = sensor.temperature()
    h = sensor.humidity()
    print("Temperature: {}".format(t))
    print("Humidity: {}".format(h))
    sleep(2)