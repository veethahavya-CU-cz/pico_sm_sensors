from machine import Pin, deepsleep, lightsleep
from time import sleep

led = Pin('LED', Pin.OUT)

while True:
    for _ in range(7):
        led.toggle()
        sleep(0.1)
    led.off()
    # deepsleep(5_000)
    lightsleep(5_000)