from machine import Pin, UART
from machine import deepsleep, lightsleep
from rp2 import bootsel_button
from utime import sleep as usleep
from time import sleep

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
led = Pin('LED', Pin.OUT)

n = 0
while True:
    if not bootsel_button():
        led.on()
        uart.write(f'{n}. Hello from node!\n')
        sleep(1)
        led.off()
        lightsleep(7 * 1000)
        with open('loopcount', 'a') as f:
            f.write(f'{n}\n')
        n += 1
    if bootsel_button():
        led.on()
        usleep(3)
        led.off()