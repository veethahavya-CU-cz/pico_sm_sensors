from machine import Pin, ADC, UART
from time import sleep as pause

def read_battery(uart_obj):
    def median(data):
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            return sorted_data[mid]

    interval = 1
    samples = 7

    batt_adc = ADC(3)
    readings = []
    for _ in range(samples):
        readings.append(batt_adc.read_u16())
        pause(interval)
    uart_obj.write(f"Readings: {readings}\n")

    med_readings = median(readings)
    battery_voltage = med_readings * ((3 * 3 * 3.3) / (65536 * 0.79))
    battery_percentage = (battery_voltage - 3.2) / (4.2 - 3.3) * 100

    uart_obj.write(f"Median reading: {med_readings}\n")
    uart_obj.write(f"Battery voltage: {battery_voltage}\n")
    uart_obj.write(f"Battery percentage: {battery_percentage}\n")

    return battery_voltage, battery_percentage


uart_obj = UART(0, 115200, tx=Pin(0), rx=Pin(1))
led = Pin('LED', Pin.OUT)

while True:
    led.on()
    read_battery(uart_obj)
    led.off()
    pause(5)