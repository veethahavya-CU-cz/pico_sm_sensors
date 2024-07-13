from machine import Pin, ADC
from utime import sleep
import _thread

baton = _thread.allocate_lock()

sm0_sensor = ADC(0)
sm1_sensor = ADC(1)
sensor_power = Pin(16, Pin.OUT)
sensor_power.on()

led = Pin("LED", Pin.OUT)
led.on()

def smX_read():
    while True:
        try:
            baton.acquire()
            # sensor_power.on()
            # sleep(0.1)
            voltages_u16 = []
            voltages_u16.append(sm0_sensor.read_u16())
            # sensor_power.off()
            print(voltages_u16[-1])
            sleep(0.1)
            baton.release()
        except KeyboardInterrupt:
            print(f"[0] Min: {min(voltages_u16)}\nMax: {max(voltages_u16)}\nAbs. difference: {max(voltages_u16) - min(voltages_u16)}\nRelative difference: {(max(voltages_u16) - min(voltages_u16)) / min(voltages_u16) * 100}%")
        finally:
            led.off()

sensor_power.on()
while True:
    try:
        baton.acquire()
        # sensor_power.on()
        # sleep(0.1)
        voltages_u16 = []
        voltages_u16.append(sm1_sensor.read_u16())
        # sensor_power.off()
        print(voltages_u16[-1])
        sleep(0.1)
        baton.release()

    except KeyboardInterrupt:
        sensor_power.off()
        led.off()
    
    finally:
        sensor_power.off()
        led.off()