from arduino import Arduino
import time

# Connect to Arduino
a = Arduino()

# Turn LED on
print('LED On')
a.led(100)

# Taper LED off
for i in range(100,0,-1):
    print('LED Power ' + str(i))
    time.sleep(0.1)
    a.led(i)

# Turn LED off
a.led(0)
