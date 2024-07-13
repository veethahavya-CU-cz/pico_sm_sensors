from machine import Pin, UART

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
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