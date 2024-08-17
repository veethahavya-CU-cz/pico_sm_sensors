from machine import ADC, Pin
from time import sleep

# while True:
#     conversion_factor = 3 * 3.3 / 65535
#     vsys = ADC(29)
#     voltage = vsys.read_u16() * conversion_factor
#     Pin(29, Pin.ALT, pull=Pin.PULL_DOWN, alt=7)
#     print(voltage)
#     sleep(0.5)



# https://forums.raspberrypi.com/viewtopic.php?t=301152

while True:
    voltage = ADC(3).read_u16() * ((3*3.3) / 2**16)
    temperature = 27 - (ADC(4).read_u16() * (3.3 / 2**16) - 0.706) / 0.001721
    print(voltage, temperature)
    sleep(0.5)