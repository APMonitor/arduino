# -*- coding: utf-8 -*-

from arduino import Arduino
import numpy as np
import time

# Loop until user breaks with ctrl c'
i = 1

while True:
    print('Testing Arduino # ' + str(i))
    
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
            time.sleep(10)
            # Check to see if temp is higher by at least 2 K
            temp1_1 = a.readTemp()
            if(temp1_1 - temp1_0 < 0.5):
                print('Transistor 1 not heating')
                successful = 0
            # Turn off transistor
            a.writeVoltage(0)
                
            # Test Transistor 2
            temp2_0 = a.readTemp2()
            # Full power
            a.writeVoltage2(255)
            time.sleep(10)
            # Check to see if temp is higher by at least 2 K
            temp2_1 = a.readTemp2()
            if(temp2_1 - temp2_0 < 0.5):
                print('Transistor 2 not heating')
                successful = 0
            # Turn off transistor
            a.writeVoltage2(0)
                
        # Shutdown Arduino
        a.close()
                
    if(successful==1):
        print('***************')
        print('All tests passed')
        print('***************')
    else:
        print('**************')
        print('TESTING FAILED')
        print('**************')
        
    i = i + 1
    # Check to see if user is finised testing
    answer = input('Test another board?  (y/n): ')
    if(answer=='n'):
        print('Exiting...')
        break