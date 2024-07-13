from machine import Pin, PWM
from utime import sleep
from neopixel import NeoPixel


def neo_off(neo):
    for i in range(8):
        neo[i] = (0, 0, 0)
    neo.write()

def neo_on(neo, color):
    for i in range(8):
        neo[i] = color
    neo.write()

def neo_toggle(neo):
    for i in range(8):
        r, g, b = neo[i]
        neo[i] = (g, b, r)
    neo.write()

def buzzer_beep(buzzer, freq, duty, duration):
    try:
        buzzer.freq(freq)
        buzzer.duty_u16(duty)
        sleep(duration)
        buzzer.duty_u16(0)
    except KeyboardInterrupt:
        buzzer.duty_u16(0)

led = Pin("LED", Pin.OUT)
neoled = NeoPixel(Pin(28, Pin.OUT), 8)
buzzer = PWM(Pin(18))

print("LED starts flashing...")
buzzer_beep(buzzer, 1000, 19660, 0.05)
neo_on(neoled, (0, 3, 0))
sleep(0.5)

for i in range(20,20000, 100):
    buzzer_beep(buzzer, i, 10000, 0.001)
    sleep(0.01)
try:
    while True:
        led.toggle()
        neo_toggle(neoled)
        sleep(0.5)
except KeyboardInterrupt:
    led.off()
    neo_off(neoled)
    buzzer.duty_u16(0)
finally:
    led.off()
    neo_off(neoled)
    buzzer_beep(buzzer, 300, 19660, 0.05)
    print("Finished.")