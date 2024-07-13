import machine
import utime
import _thread
# We configure the pin of the internal led as an output and
# we assign to internal_led
internal_led = machine.Pin(25, machine.Pin.OUT)
# We create a semaphore (A.K.A lock)
baton = _thread.allocate_lock()
# Function that will block the thread with a while loop
# which will simply display a message every second
def second_thread():
    while True:
        # We acquire the traffic light lock
        baton.acquire()
        print("Hello, I'm here in the second thread writting every second")
        utime.sleep(1)
        # We release the traffic light lock
        baton.release()
# Function that initializes execution in the second core
# The second argument is a list or dictionary with the arguments
# that will be passed to the function.
_thread.start_new_thread(second_thread, ())
# Second loop that will block the main thread, and what it will do
# that the internal led blinks every half second
while True:
    # We acquire the semaphore lock
    baton.acquire()
    internal_led.toggle()
    utime.sleep(0.25)
    # We release the semaphore lock
    baton.release()