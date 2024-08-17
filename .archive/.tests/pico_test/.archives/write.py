from machine import Pin
import utime

led = Pin("LED", Pin.OUT)
led.on()

fsm = open('sm.txt', 'w')
ftemp = open('temp.txt', 'w')
frh = open('rh.txt', 'w')

try:
    for i in range(6*24*30*6):
        fsm.write(f"{utime.time()} 0.5456 50236\n")
    for i in range(1*24*30*6):
        ftemp.write(f"{utime.time()} 25.55\n")
        frh.write(f"{utime.time()} 33\n")
except KeyboardInterrupt:
    pass
finally:
    fsm.close()
    ftemp.close()
    frh.close()
    led.off()