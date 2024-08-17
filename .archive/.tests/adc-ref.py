from machine import Pin, ADC   # type: ignore
from time import sleep
import math

def standard_deviation(data):
    n = len(data)
    if n < 2:
        return 0.0
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / (n - 1)
    return math.sqrt(variance)

def adc_power(mode, power_pin=None):
    if mode == 'PFM':
        pass
    elif mode == 'PWM':
        # Set pin 23 as output and set it to high
        smps_pin = Pin(23, Pin.OUT)
        smps_pin.value(1)
    elif mode == 'GPIO':
        if not power_pin:
            print("Power pin not specified.")
            return
        else:
            power_pin = Pin(power_pin, Pin.OUT)
            power_pin.value(1)
    elif mode == '3V3':
        pass
    elif mode == 'VBUS':
        pass
    else:
        print("Invalid mode. Choose 'PFM' or 'PWM'.")


# Setup pin 26 as input and pin 23 as output
adc_pin = Pin(26, Pin.IN)

vals = []
n = 0

power_mode = 'PWM'
adc_power(power_mode, 15)
sleep(0.5)

# Main loop
while n < 1_000:
    try:
        # Read analog value from pin 26
        analog_value = ADC(26).read_u16()
        vals.append(analog_value)

        # Print the analog value
        print(analog_value)

        # Delay for 100 milliseconds
        sleep(0.1)
        n += 1
        exit_code = 0

    except KeyboardInterrupt:
        print(f"\n\n\n{power_mode} Mode:")
        print(f"    Min: {min(vals)}\n    Max: {max(vals)}\n    Difference: {max(vals) - min(vals)}\n    Percent Difference: {(max(vals) - min(vals)) / min(vals) * 100:.2f}%\n    Average: {sum(vals) / len(vals)}\n    Std. Dev.: {standard_deviation(vals)}")
        exit_code = 1
        break

if not exit_code:
    print(f"\n\n\n{power_mode} Mode:")
    print(f"    Min: {min(vals)}\n    Max: {max(vals)}\n    Difference: {max(vals) - min(vals)}\n    Percent Difference: {(max(vals) - min(vals)) / min(vals) * 100:.2f}%\n    Average: {sum(vals) / len(vals)}\n    Std. Dev.: {standard_deviation(vals)}")



'''
--- [Aggregated] Test Results [t = 100 s] ---

---------------------------------
Sorted by Std. Dev.:
    PWM Mode: 84.659615
    GPIO Mode: 86.480735
    3V3 Mode: 88.1571
    VBUS Mode: 92.9627
    PFM Mode: 97.163415

Sorted by Percent Difference:
    PWM Mode: 2.335%
    PFM Mode: 2.95%
    3V3 Mode: 3.01%
    GPIO Mode: 3.02%
    VBUS Mode: 3.845%
---------------------------------



--- [Dry] Test Results [t = 100 s] ---

---------------------------------
Sorted by Std. Dev.:
    VBUS Mode: 59.7636
    PWM Mode: 77.66348
    3V3 Mode: 80.16315
    GPIO Mode: 86.76765
    PFM Mode: 89.23343

Sorted by Percent Difference:
    PWM Mode: 0.91%
    PFM Mode: 1.00%
    GPIO Mode: 1.65%
    3V3 Mode: 1.88%
    VBUS Mode: 1.91%
---------------------------------

PFM Mode:
    Min: 54061
    Max: 55677
    Difference: 1616
    Percent Difference: 1.00%
    Average: 54649.27
    Std. Dev.: 89.23343
PWM Mode:
    Min: 53837
    Max: 55309
    Difference: 1472
    Percent Difference: 0.91%
    Average: 54655.35
    Std. Dev.: 77.66348
3V3 Mode:
    Min: 56269
    Max: 57325
    Difference: 1056
    Percent Difference: 1.88%
    Average: 56791.08
    Std. Dev.: 80.16315
GPIO Mode:
    Min: 53293
    Max: 54173
    Difference: 880
    Percent Difference: 1.65%
    Average: 53695.57
    Std. Dev.: 86.76765
VBUS Mode:
    Min: 56989
    Max: 58078
    Difference: 1089
    Percent Difference: 1.91%
    Average: 57344.59
    Std. Dev.: 59.7636



--- [Wet] Test Results [t = 100 s] ---

---------------------------------
Sorted by Std. Dev.:
    GPIO Mode: 86.19382
    PWM Mode: 91.65575
    3V3 Mode: 96.15105
    PFM Mode: 105.0934
    VBUS Mode: 126.1618

Sorted by Percent Difference:
    PWM Mode: 3.76%
    3V3 Mode: 4.14%
    GPIO Mode: 4.39%
    PFM Mode: 4.90%
    VBUS Mode: 5.78%
---------------------------------

PWM Mode:
    Min: 25126
    Max: 26070
    Difference: 944
    Percent Difference: 3.76%
    Average: 25606.27
    Std. Dev.: 91.65575
PFM Mode:
    Min: 25142
    Max: 26374
    Difference: 1232
    Percent Difference: 4.90%
    Average: 25642.5
    Std. Dev.: 105.0934
3V3 Mode:
    Min: 25094
    Max: 26134
    Difference: 1040
    Percent Difference: 4.14%
    Average: 25693.18
    Std. Dev.: 96.15105
GPIO Mode:
    Min: 23301
    Max: 24325
    Difference: 1024
    Percent Difference: 4.39%
    Average: 23820.95
    Std. Dev.: 86.19382
VBUS Mode:
    Min: 25174
    Max: 26630
    Difference: 1456
    Percent Difference: 5.78%
    Average: 26089.86
    Std. Dev.: 126.1618

'''