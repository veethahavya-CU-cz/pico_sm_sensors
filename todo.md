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