# TODO: cehck if connected to USB

```Python
import sys

def usb_connected():
    try:
        sys.stdin.read(1)  # Attempt to read from USB serial input
        return True
    except OSError:  # Will raise OSError if USB is not connected
        return False

if usb_connected():
    print("USB connected")
else:
    print("USB not connected")
```

# [ ] add a temperature sensor to calibrate the SMS
https://randomnerdtutorials.com/raspberry-pi-pico-ds18b20-micropython/#Rpi-Pico-multiple-ds18b20-sensors-wiring
https://www.laskakit.cz/dallas-digitalni-vodotesne-cidlo-teploty-ds18b20-1m/
