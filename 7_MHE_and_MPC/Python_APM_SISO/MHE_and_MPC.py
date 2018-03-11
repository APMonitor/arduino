import tclab
import numpy as np
import time
from APMonitor.apm import *
import matplotlib.pyplot as plt

# Connect to Arduino
a = tclab.TCLab()

# Run time in minutes
run_time = 10.0

# Number of cycles
loops = int(20.0*run_time)

# Temperature (K)
T1 = np.ones(loops) * a.T1 # measured T
Tsp1 = np.ones(loops) * a.T1 # measured T

# milli-volts input
Q1 = np.ones(loops) * 0.0
Q2 = np.ones(loops) * 0.0

# time
tm = np.zeros(loops)

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

desiredTemp = 40.0
sphi = desiredTemp + 1.0
splo = desiredTemp - 1.0
apm_option(s,c,'TC.sphi',sphi)
apm_option(s,c,'TC.splo',splo)

# Main Loop
Tsp_new = 30.0
Tsp_old = Tsp_new
params = np.zeros(4) # [0.36,47.73,1.56,300.0]
start_time = time.time()
prev_time = start_time

print('Running Main Loop. Ctrl-C to end.')
print('  Time   Q1     Q2    T1     T1 SP')
print('{:6.1f} {:6.2f} {:6.2f} {:6.2f} {:6.2f}'.format(tm[0], \
                                                       Q1[0], \
                                                       Q2[0], \
                                                       T1[0], \
                                                       Tsp1[0]))

try:
    for i in range(loops-1):
        # Sleep time
        sleep_max = 3.0 
        sleep = sleep_max - (time.time() - prev_time)
        if sleep>=0.01:
            time.sleep(sleep)
        else:
            time.sleep(0.01)

        # Record time and change in time
        t = time.time()
        tm[i] = t - start_time
        dt = t - prev_time
        prev_time = t
                    
        # Read temperature in degC
        T1[i] = a.T1

        # MHE - match model to measurements
        if i%2==0:
            # run MHE every 2 seconds (see mhe.csv)
            params = mhe(T1[i],Q1[i-1])

        # MPC
        # change setpoints
        if i==10:
            Tsp_new = 35.0
        if i==50:
            Tsp_new = 50.0
        if i==100:
            Tsp_new = 40.0
        if i==150:
            Tsp_new = 55.0
        # change in setpoint
        if Tsp_new != Tsp_old:
            apm_option(s,c,'TC.sphi',Tsp_new+0.1)
            apm_option(s,c,'TC.splo',Tsp_new-0.1)
            Tsp_old = Tsp_new
        Tsp1[i] = Tsp_new
        # run MPC            
        Q1[i] = mpc(T1[i],params)

        # Write output (0-100%)
        Q1[i] = min(100.0,max(0.0,Q1[i]))
        a.Q1(Q1[i])

        # Print line of data
        print('{:6.1f} {:6.2f} {:6.2f} {:6.2f} {:6.2f}'.format(tm[i], \
                                                               Q1[i], \
                                                               Q2[i], \
                                                               T1[i], \
                                                               Tsp1[i]))

        # Plot
        plt.clf()
        ax=plt.subplot(2,1,1)
        ax.grid()
        plt.plot(tm[0:i],T1[0:i],'ro',MarkerSize=3,label=r'$T_1$')
        plt.plot(tm[0:i],Tsp1[0:i],'b-',MarkerSize=3,label=r'$T_1 Setpoint$')
        plt.ylabel('Temperature (degC)')
        plt.legend(loc='best')
        ax=plt.subplot(2,1,2)
        ax.grid()
        plt.plot(tm[0:i],Q1[0:i],'r-',LineWidth=3,label=r'$Q_1$')
        plt.plot(tm[0:i],Q2[0:i],'b:',LineWidth=3,label=r'$Q_2$')
        plt.ylabel('Heaters')
        plt.xlabel('Time (sec)')
        plt.legend(loc='best')
        plt.draw()
        plt.pause(0.05)

        # Open Web-Plots
        if i==3:
            apm_web(s,c)

        if i==10:
            apm_web(s,b)

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
