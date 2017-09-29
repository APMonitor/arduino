from arduino import Arduino
import numpy as np
import time

# Connect to Arduino
a = Arduino()

# Set up plotting
a.initPlots()

# Run time in minutes
run_time = 10.0

# Number of cycles
loops = int(60.0*run_time)

# Temperature (K)
Tsp1 = np.ones(loops) * 320.0 # set point
T1 = np.ones(loops) * a.readTemp() # measured T

Tsp2 = np.ones(loops) * 300.0 # set point
T2 = np.ones(loops) * a.readTemp2() # measured T

# milli-volts step test (0 - 150 mV)
mV1 = np.ones(loops) * 0.0
mV1[20:] = 150.0

mV2 = np.ones(loops) * 0.0
mV2[60:] = 120.0

# Main Loop
start_time = time.time()
prev_time = start_time
try:
    print('Running Main Loop. Ctrl-C to record data and end.')
    print('      Time  milliVolt Temperature  milliVolt Temperature')
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
                        
            # Read temperatures in Kelvin 
            T1[i] = a.readTemp()
            T2[i] = a.readTemp2() 

            ###############################
            ### CONTROLLER or ESTIMATOR ###
            ###############################

            # Write output in milliVolts (0-250)
            mV1[i] = min(250.0,max(0.0,mV1[i]))
            a.writeVoltage(int(mV1[i]))

            mV2[i] = min(250.0,max(0.0,mV2[i]))
            a.writeVoltage2(int(mV2[i]))

            # Add data to array
            newData = np.array([[tm,mV1[i],T1[i],Tsp1[i],mV2[i],T2[i],Tsp2[i]]])
            print('{:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f}'.format(tm,mV1[i],T1[i],mV2[i],T2[i]))
            a.addData(newData)
            
            # Update plots
            a.updatePlots()

    # Write data to file
    a.saveData()
    
# Allow user to end loop with Ctrl-C           
except KeyboardInterrupt:
    # Write data to file
    a.saveData()
    # Disconnect from Arduino
    a.writeVoltage(0)
    a.writeVoltage2(0)
    print('Shutting down')
    a.close()
    
# Make sure serial connection still closes when there's an error
except:           
    # Disconnect from Arduino
    a.writeVoltage(0)
    a.writeVoltage2(0)
    print('Error: Shutting down')
    a.close()
    raise
