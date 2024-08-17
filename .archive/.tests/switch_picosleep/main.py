from machine import Pin
from time import sleep as pause
# from picosleep import seconds as sleep
from machine import deepsleep as sleep


power_switch = Pin(0, Pin.IN, Pin.PULL_UP)
led = Pin('LED', Pin.OUT)

led.off()

while True:
    while power_switch.value():
        for _ in range(7):
            led.toggle()
            pause(0.1)
        led.off()
        sleep(5)
    while not power_switch.value():
        for _ in range(7):
            led.toggle()
            pause(0.5)
        led.off()
        pause(5)
    led.off()