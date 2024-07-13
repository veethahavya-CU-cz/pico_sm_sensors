from machine import Pin, UART
from time import sleep

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
led = Pin('LED', Pin.OUT)

n = 0
while True:
    try:
        led.on()
        uart.write(f'{n}. Hello from node!\n')
        sleep(1)
        led.off()
        n += 1
    except Exception as e:
        uart.write(f'Error: {e}\n')
        print(e)
    finally:
        led.off()