from machine import Pin
from time import sleep

led = Pin('LED', Pin.OUT)

for _ in range(7):    
    led.on()
    sleep(0.1)
    led.off()
    sleep(0.1)

sleep(1)