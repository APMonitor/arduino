from arduino import Arduino
import numpy as np
import time
from apm import *

# Connect to Arduino
a = Arduino()

# Set up plotting
a.initPlots()

# Run time in minutes
run_time = 10.0

# Number of cycles
loops = int(60.0*run_time)

# Temperature (K)
T = np.ones(loops) * a.readTemp() # measured T

# milli-volts input
mV = np.ones(loops) * 0.0

# moving horizon estimation
from mhe import *
s = 'http://byu.apmonitor.com'
b = 'mhe'
mhe_init()

# Main Loop
Vin = 0.0
start_time = time.time()
prev_time = start_time
try:
    print('Running Main Loop. Ctrl-C to end.')
    print('      Time  milliVolt Temp (F)    Gain (K)       tau        zeta       TK_ss')
    for i in range(loops-1):
            # Sleep time
            sleep_max = 1.0 
            sleep = sleep_max - (time.time() - prev_time)
            if sleep>=0.01:
                time.sleep(sleep)
            else:
                time.sleep(0.01)

            # Record time and change in time
            tm = time.time() - start_time
            dt = time.time() - prev_time
            prev_time = time.time()
                        
            # Read temperature in Kelvin 
            T[i] = a.readTemp()

            # MHE - match model to measurements
            if i%2==0:
                # run MHE every 2 seconds (see mhe.csv)
                K, tau, zeta, TK_ss = mhe(T[i],Vin)

            # manual mode step for the input
            if i==10:
                Vin = 150.0
            if i==200:
                Vin = 10.0
            if i==400:
                Vin = 150.0

            # Write output in milliVolts (0-255)
            mV[i] = min(150.0,max(0.0,Vin))
            a.writeVoltage(mV[i])

            # Add data to array
            newData = np.array([[tm,mV[i],T[i],320.0]])
            print('{:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f}'.format(tm,mV[i],T[i],K,tau,zeta,TK_ss))
            a.addData(newData)
            
            # Update plots
            a.updatePlots()

            # Open web-viewer on 10th cycle
            if i==10:
                apm_web(s,b)


    # Write data to file
    a.saveData()
    
# Allow user to end loop with Ctrl-C           
except KeyboardInterrupt:
    # Write data to file
    a.saveData()
    # Disconnect from Arduino
    a.writeVoltage(0)
    print('Shutting down')
    a.close()
    
# Make sure serial connection still closes when there's an error
except:           
    # Disconnect from Arduino
    a.writeVoltage(0)
    print('Shutting down')
    a.close()
    raise
else:
    # Disconnect from Arduino
    a.writeVoltage(0)
    print('Shutting down')
    a.close()
    raise
