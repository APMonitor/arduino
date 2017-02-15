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

# model predictive control
from mpc import *
s = 'http://byu.apmonitor.com'
c = 'mpc'
mpc_init()

desiredTemp = 320.0
sphi = desiredTemp + 1.0
splo = desiredTemp - 1.0
apm_option(s,c,'TK.sphi',sphi)
apm_option(s,c,'TK.splo',splo)

# Main Loop
Vin = 0.0
Tsp_new = 100.0
Tsp_old = Tsp_new
params = np.zeros(4) # [0.36,47.73,1.56,300.0]
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
                params = mhe(T[i],Vin)

            # MPC
            # change setpoints
            if i==1:
                Tsp_new = 320.0
            if i==180:
                Tsp_new = 310.0
            # change in setpoint
            if Tsp_new != Tsp_old:
                apm_option(s,c,'TK.sphi',Tsp_new+0.1)
                apm_option(s,c,'TK.splo',Tsp_new-0.1)
                Tsp_old = Tsp_new
            # run MPC            
            Vin = mpc(T[i],params)

            # Write output in milliVolts (0-255)
            mV[i] = min(150.0,max(0.0,Vin))
            a.writeVoltage(mV[i])

            # Add data to array
            newData = np.array([[tm,mV[i],T[i],Tsp_new]])
            print('{:10.2f} {:10.2f} {:10.2f} {:10.2f}'.format(tm,mV[i],T[i],Tsp_new))
            a.addData(newData)
            
            # Update plots
            a.updatePlots()

            # Open web-viewer on 10th cycle
            if i==10:
                apm_web(s,b)

            # Open MPC web-viewer on 20th cycle
            if i==20:
                apm_web(s,c)

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
