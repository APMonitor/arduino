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
Tsp = np.ones(loops) * 320.0 # set point
T = np.ones(loops) * a.readTemp() # measured T

# milli-volts step test (0 - 255 mV)
mV = np.ones(loops) * 0.0

# Main Loop
Vin = 0.0
start_time = time.time()
prev_time = start_time
try:
    print('Running Main Loop. Ctrl-C to end.')
    print('      Time  milliVolt Temperature')
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
            # Temperature in Fahrenheit
            Tf = (T[i]-273.0)*9.0/5.0+32.0            

            ##############################################
            # on / off control
            ##############################################
            if Tf <= 120.0:
                Vin = 150.0
            else:
                Vin = 0.0

            # Write output in milliVolts (0-255)
            # limit to 150 to avoid overheating
            mV[i] = min(150.0,max(0.0,Vin))
            a.writeVoltage(mV[i])

            # Add data to array
            newData = np.array([[tm,mV[i],T[i],Tsp[i]]])
            print('{:10.2f} {:10.2f} {:10.2f}'.format(tm,mV[i],T[i]))
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
