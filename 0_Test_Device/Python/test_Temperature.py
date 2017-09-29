from arduino import Arduino
import time

# Connect to Arduino
a = Arduino()

# Read temperature 1
TF = a.readTempF()
TC = a.readTempC()
print('Temperature 1: ' + str(TC) + ' degC or ' + str(TF) + ' degF')

# Read temperature 2
TF2 = a.readTempF2()
TC2 = a.readTempC2()
print('Temperature 2: ' + str(TC2) + ' degC or ' + str(TF2) + ' degF')


# Turn on heaters (0-255)
a.writeVoltage(250)
a.writeVoltage2(150)

# Turn on LED
a.led(100)

# Wait 20 seconds
print('Heating for 20 seconds')
time.sleep(20)

# Turn off LED
a.led(0)

# Turn off heaters
a.writeVoltage(0)
a.writeVoltage2(0)


# Read temperature 1
TF = a.readTempF()
TC = a.readTempC()
print('Temperature 1: ' + str(TC) + ' degC or ' + str(TF) + ' degF')

# Read temperature 2
TF2 = a.readTempF2()
TC2 = a.readTempC2()
print('Temperature 2: ' + str(TC2) + ' degC or ' + str(TF2) + ' degF')
