import tclab
import numpy as np
import time
import matplotlib.pyplot as plt
from gekko import GEKKO

# Connect to Arduino
a = tclab.TCLab()

# Get Version
print(a.version)

# Turn LED on
print('LED On')
a.LED(100)

# Run time in minutes
run_time = 5.0

# Number of cycles
loops = int(60.0*run_time)
tm = np.zeros(loops)

# Temperature (K)
T1 = np.ones(loops) * a.T1 # temperature (degC)
Tsp1 = np.ones(loops) * 30.0 # set point (degC)
# Set point changes
Tsp1[100:] = 40.0
Tsp1[200:] = 35.0

T2 = np.ones(loops) * a.T2 # temperature (degC)
Tsp2 = np.ones(loops) * 23.0 # set point (degC)

# heater values
Q1s = np.ones(loops) * 0.0
Q2s = np.ones(loops) * 0.0

#########################################################
# Initialize Model as Estimator
#########################################################
m = GEKKO(name='tclab-mpc')

# 30 second time horizon
m.time = np.linspace(0,30,31)

# Parameters
Q1_ss = m.Param(value=0)
TC1_ss = m.Param(value=23)
Kp = m.Param(value=0.4)
tau = m.Param(value=160.0)

# Manipulated variable
Q1 = m.MV(value=0)
Q1.STATUS = 1  # use to control temperature
Q1.FSTATUS = 0 # no feedback measurement
Q1.LOWER = 0.0
Q1.UPPER = 100.0
Q1.DMAX = 50.0
Q1.COST = 0.0
Q1.DCOST = 1.0e-4

# Controlled variable
TC1 = m.CV(value=TC1_ss)
TC1.STATUS = 1     # minimize error with setpoint range
TC1.FSTATUS = 1    # receive measurement
TC1.TR_INIT = 2    # reference trajectory
TC1.TAU = 10       # time constant for response

# Equation
m.Equation(tau * TC1.dt() + (TC1-TC1_ss) == Kp * (Q1-Q1_ss))  

# Global Options
#m.server = 'http://127.0.0.1' # local server, if available
m.options.IMODE   = 6 # MPC
m.options.CV_TYPE = 1 # Objective type
m.options.NODES   = 3 # Collocation nodes
m.options.SOLVER  = 1 # 1=APOPT, 3=IPOPT
##################################################################

# Create plot
plt.figure()
plt.ion()
plt.show()

# Main Loop
start_time = time.time()
prev_time = start_time
try:
    for i in range(1,loops):
        # Sleep time
        sleep_max = 1.0
        sleep = sleep_max - (time.time() - prev_time)
        if sleep>=0.01:
            time.sleep(sleep)
        else:
            time.sleep(0.01)

        # Record time and change in time
        t = time.time()
        dt = t - prev_time
        prev_time = t
        tm[i] = t - start_time
                    
        # Read temperatures in Kelvin 
        T1[i] = a.T1
        T2[i] = a.T2

        ###############################
        ### MPC CONTROLLER          ###
        ###############################
        TC1.MEAS = T1[i]
        # input setpoint with deadband +/- DT
        DT = 0.1
        TC1.SPHI = Tsp1[i] + DT
        TC1.SPLO = Tsp1[i] - DT
        # solve MPC
        m.solve(disp=False)    
        # test for successful solution
        if (m.options.APPSTATUS==1):
            # retrieve the first Q value
            Q1s[i] = Q1.NEWVAL
        else:
            # not successful, set heater to zero
            Q1s[i] = 0        
        
        # Write output (0-100)
        a.Q1(Q1s[i])
        a.Q2(Q2s[i])

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
        plt.plot(tm[0:i],Q1s[0:i],'r-',LineWidth=3,label=r'$Q_1$')
        plt.plot(tm[0:i],Q2s[0:i],'b:',LineWidth=3,label=r'$Q_2$')
        plt.ylabel('Heaters')
        plt.xlabel('Time (sec)')
        plt.legend(loc='best')
        plt.draw()
        plt.pause(0.05)

    # Turn off heaters
    a.Q1(0)
    a.Q2(0)
    print('Shutting down')
        
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
