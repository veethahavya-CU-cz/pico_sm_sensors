from machine import Pin
from utime import sleep
# import picosleep
from machine import deepsleep, lightsleep

led = Pin("LED", Pin.OUT)
led.off()

while True:
    for i in range(3):
        led.value(1)
        sleep(0.1)
        led.value(0)
        sleep(0.1)
    led.off()

    sleep(3)

    # deepsleep(3 * 1000)
    # lightsleep(3 * 1000)
    # picosleep.seconds(3)

    for i in range(7):
        led.value(1)
        sleep(0.1)
        led.value(0)
        sleep(0.1)
    led.off()