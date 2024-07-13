from machine import Pin, ADC
from utime import sleep, time
from neopixel import NeoPixel


def neo_off(neo):
    for i in range(8):
        neo[i] = (0, 0, 0)
    neo.write()

def neo_on(neo, color):
    for i in range(8):
        neo[i] = color
    neo.write()


start_time = time()

sm_sensor = ADC(Pin(26))
# sensor_power = Pin(27, Pin.OUT, Pin.PULL_UP)
smps_mode_pin = Pin(23, Pin.OUT)

led = Pin("LED", Pin.OUT)
neoled = NeoPixel(Pin(28, Pin.OUT), 8)
exit_button = Pin(20, Pin.IN, Pin.PULL_DOWN)


while exit_button.value():
    neo_on(neoled, (0, 255, 0))
    led.on()
    # sensor_power.on()
    smps_mode_pin.value(1)
    sleep(0.1)

    voltages_u16 = []
    for i in range(100):
        voltages_u16.append(sm_sensor.read_u16())
        sleep(1e-3)
    mean = (sum(voltages_u16) / len(voltages_u16)) / 65535

    with open("sm.csv", "a") as f:
        f.write(f"{time()-start_time}; {mean}\n")
    print(f"{time()-start_time}; {mean}")

    del voltages_u16, mean

    # sensor_power.off()
    smps_mode_pin.value(0)
    led.off()
    neo_off(neoled)
    sleep(0.5)