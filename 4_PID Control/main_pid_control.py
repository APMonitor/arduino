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

######################################
# PID configuration
######################################
# From first-order plus dead-time (FOPDT) regression 
Kp = 0.3622
taup = 137.85
thetap = 16.00
# PID Tuning Parameters
Kc = 1.0/Kp  * 2.0
tauI = taup  / 2.0
tauD = 0.0
# Upper and Lower limits on OP
op_hi = 150.0
op_lo = 0.0
# storage for recording values
ns = loops
op = np.zeros(ns+1)  # controller output
pv = np.zeros(ns+1)  # process variable
e = np.zeros(ns+1)   # error
ie = np.zeros(ns+1)  # integral of the error
dpv = np.zeros(ns+1) # derivative of the pv
P = np.zeros(ns+1)   # proportional
I = np.zeros(ns+1)   # integral
D = np.zeros(ns+1)   # derivative
# set points for controller
sp = np.ones(ns+1)*300.0  # set point (K)
sp[5:200] = 320.0
sp[200:] = 310.0

try:
    print('Running Main Loop. Ctrl-C to end.')
    print('      Time  milliVolt   Temp (K)     SP (K)       P          I           D')
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
            # PID control
            ##############################################
            pv[i] = T[i]
            e[i] = sp[i] - pv[i]
            if i >= 1:  # calculate starting on second cycle
                dpv[i] = (pv[i]-pv[i-1])/dt
                ie[i] = ie[i-1] + e[i] * dt
            P[i] = Kc * e[i]
            I[i] = Kc/tauI * ie[i]
            D[i] = - Kc * tauD * dpv[i]
            op[i] = op[0] + P[i] + I[i] + D[i]
            if op[i] > op_hi:  # check upper limit
                op[i] = op_hi
                ie[i] = ie[i] - e[i] * dt # anti-reset windup
            if op[i] < op_lo:  # check lower limit
                op[i] = op_lo
                ie[i] = ie[i] - e[i] * dt # anti-reset windup
            Vin = op[i]

            # Write output in milliVolts (0-255)
            # limit to 150 to avoid overheating
            mV[i] = min(150.0,max(0.0,Vin))
            a.writeVoltage(mV[i])

            # Add data to array
            newData = np.array([[tm,mV[i],T[i],Tsp[i]]])
            print('{:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f}'.format(tm,mV[i],T[i],sp[i],P[i],I[i],D[i]))
            a.addData(newData)
            
            # Update plots
            a.updatePlots()

    # fill in last points from prior points
    op[ns] = op[ns-1]
    ie[ns] = ie[ns-1]
    P[ns] = P[ns-1]
    I[ns] = I[ns-1]
    D[ns] = D[ns-1]

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
