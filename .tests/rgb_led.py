from machine import Pin, PWM
import time

# Setup PWM on each pin with hardcoded values
r = PWM(Pin(14))
g = PWM(Pin(13))
b = PWM(Pin(12))

r.freq(1000)
g.freq(1000)
b.freq(1000)

def led(color_name, display_time=1, auto_off=True):
    colors = {
        'red': (65535, 0, 0),
        'green': (0, 21845, 0),
        'blue': (0, 0, 32767),
        'cyan': (0, 32767, 32767),
        'yellow': (65535, 13107, 0),
        'magenta': (65535, 0, 32767),
        'white': (65535, 32767, 32767),
        'orange': (65535, 6553, 0),
        'pink': (65535, 8192, 13107),
        'lightblue': (32767, 32767, 65535),
        'lightgreen': (32767, 49150, 3276),
        'off': (0, 0, 0)
    }
    if color_name in colors:
        print('LED color:', color_name)
        r.duty_u16(colors[color_name][0])
        g.duty_u16(colors[color_name][1])
        b.duty_u16(colors[color_name][2])
        time.sleep(display_time)
        if auto_off:
            r.duty_u16(0)
            g.duty_u16(0)
            b.duty_u16(0)