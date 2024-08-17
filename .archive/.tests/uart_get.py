from machine import Pin, UART

uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
led = Pin('LED', Pin.OUT)

while True:
    try:
        led.on()
        if uart.any():
            data = uart.read()

            if data:
                print(data.decode('utf-8'))
    except Exception as e:
        print(e)
    finally:
        led.off()