import tclab
import numpy as np
import time
from APMonitor.apm import *
import matplotlib.pyplot as plt

# Connect to Arduino
a = tclab.TCLab()

# Run time in minutes
run_time = 10.0

# Number of cycles (1 cycle per 2 seconds)
loops = int(30.0*run_time)

# Temperature (K)
T1 = np.ones(loops) * a.T1 # measured T
T1mhe = np.ones(loops) * a.T1 # measured T
Tsp1 = np.ones(loops) * a.T1 # measured T
Kp = np.ones(loops) * 0.3598
tau = np.ones(loops) * 47.73
zeta = np.ones(loops) * 1.56
TC_ss = np.ones(loops) * 23

# milli-volts input
Q1 = np.ones(loops) * 0.0
Q2 = np.ones(loops) * 0.0
Q1[6:] = 100.0
Q1[50:] = 20.0
Q1[100:] = 80.0
Q1[150:] = 10.0
Q1[200:] = 95.0
Q1[250:] = 0.0

# time
tm = np.zeros(loops)

# moving horizon estimation
from mhe import *
s = 'http://byu.apmonitor.com'
b = 'mhe'
mhe_init()

# Main Loop
start_time = time.time()
prev_time = start_time

try:
    for i in range(loops-1):
        # Sleep time
        sleep_max = 2.0 
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
        # run MHE every 2 seconds (see mhe.csv)
        params = mhe(T1[i],Q1[i-1])
        Kp[i] = params[0]
        tau[i] = params[1]
        zeta[i] = params[2]
        TC_ss[i] = params[3]
        T1mhe[i] = params[4]

        # Write output (0-100%)
        Q1[i] = min(100.0,max(0.0,Q1[i]))
        a.Q1(Q1[i])

        # Plot
        plt.clf()
        ax=plt.subplot(4,1,1)
        ax.grid()
        plt.plot(tm[0:i],T1[0:i],'ro',MarkerSize=3,label=r'$T_1 Measured$')
        plt.plot(tm[0:i],T1mhe[0:i],'bx',MarkerSize=3,label=r'$T_1 MHE$')
        plt.ylabel('Temperature (degC)')
        plt.legend(loc='best')

        ax=plt.subplot(4,1,2)
        ax.grid()
        plt.plot(tm[0:i],Q1[0:i],'r-',MarkerSize=3,label=r'$Q_1$')
        plt.plot(tm[0:i],Q2[0:i],'b:',MarkerSize=3,label=r'$Q_2$')
        plt.ylabel('Heaters')
        plt.legend(loc='best')

        ax=plt.subplot(4,1,3)
        ax.grid()
        plt.plot(tm[0:i],Kp[0:i],'ro',MarkerSize=3,label=r'$K_p$')
        plt.plot(tm[0:i],zeta[0:i],'bx',MarkerSize=3,label=r'$\zeta$')
        plt.ylabel('Parameters')
        plt.legend(loc='best')

        ax=plt.subplot(4,1,4)
        ax.grid()
        plt.plot(tm[0:i],tau[0:i],'k^',MarkerSize=3,label=r'$\tau$')
        plt.plot(tm[0:i],TC_ss[0:i],'gs',MarkerSize=3,label=r'$TC_{ss}$')
        plt.ylabel('Parameters')
        plt.legend(loc='best')

        plt.xlabel('Time (sec)')
        plt.draw()
        plt.pause(0.05)

        # Open Web Interface
        if i==5:
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
