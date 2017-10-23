import tclab
import numpy as np
import time

try:
    # Connect to Arduino
    a = tclab.TCLab()

    # Get Version
    print(a.version)

    # Temperatures
    print('Temperatures')
    print('Temperature 1: ' + str(a.T1) + ' degC')
    print('Temperature 2: ' + str(a.T2) + ' degC')

    # Turn LED on
    print('LED On')
    a.LED(100)

    # Turn on Heaters (0-100%)
    print('Turn On Heaters (Q1=90%, Q2=80%)')
    a.Q1(90.0)
    a.Q2(80.0)

    # Sleep (sec)
    time.sleep(60.0)

    # Turn Off Heaters
    print('Turn Off Heaters')
    a.Q1(0.0)
    a.Q2(0.0)

    # Temperatures
    print('Temperatures')
    print('Temperature 1: ' + str(a.T1) + ' degC')
    print('Temperature 2: ' + str(a.T2) + ' degC')
    
# Allow user to end loop with Ctrl-C           
except KeyboardInterrupt:
    # Disconnect from Arduino
    a.Q1(0)
    a.Q2(0)
    print('Shutting down')
    a.close()
    
# Make sure serial connection still closes when there's an error
except:           
    # Disconnect from Arduino
    a.Q1(0)
    a.Q2(0)
    print('Error: Shutting down')
    a.close()
    raise
