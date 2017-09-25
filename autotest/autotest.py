# -*- coding: utf-8 -*-

from arduino import Arduino
import numpy as np
import time

successful = 1

# Try connecting to Arduino
try:
    a = Arduino()
except:
    successful = 0
    print('Could not connect to Arduino')

# Continue with tests only if Arduino is connected
if(successful==1):
    print('Testing, please wait...')
    
    # Test temperature sensor 1
    temp1 = a.readTemp()
    if(temp1 < 250 or temp1 > 450):
        print('Temperature Sensor 1 reading of ' + str(temp1) + ' is outside \
              normal operating conditions')
        successful = 0

    # Test temperature sensor 2
    temp2 = a.readTemp2()
    if(temp1 < 250 or temp1 > 450):
        print('Temperature Sensor 2 reading of ' + str(temp2) + ' is outside \
              normal operating conditions')
        successful = 0
        
    # Test transistors only if sensors are good
    if(successful==1):
        
        # Test Transistor 1
        temp1_0 = a.readTemp()
        # Full power
        a.writeVoltage(255)
        time.sleep(5)
        # Check to see if temp is higher by at least 2 K
        temp1_1 = a.readTemp()
        if(temp1_1 - temp1_0 < 2):
            print('Transistor 1 not heating')
            successful = 0
            
        # Test Transistor 2
        temp2_0 = a.readTemp2()
        # Full power
        a.writeVoltage2(255)
        time.sleep(5)
        # Check to see if temp is higher by at least 2 K
        temp2_1 = a.readTemp2()
        if(temp2_1 - temp2_0 < 2):
            print('Transistor 1 not heating')
            successful = 0
            
if(successful==1):
    print('All tests passed')
else:
    print('**************')
    print('Testing Failed')
    print('**************')