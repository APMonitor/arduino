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

# Number of cycles with 3 second intervals
loops = int(20.0*run_time)
tm = np.zeros(loops)

# Temperature (K)
T1 = np.ones(loops) * a.T1 # temperature (degC)
Tsp1 = np.ones(loops) * 35.0 # set point (degC)
T2 = np.ones(loops) * a.T2 # temperature (degC)
Tsp2 = np.ones(loops) * 23.0 # set point (degC)

# Set point changes
Tsp1[50:] = 40.0
Tsp2[10:] = 30.0 

# heater values
Q1s = np.ones(loops) * 0.0
Q2s = np.ones(loops) * 0.0

#########################################################
# Initialize Model as Estimator
#########################################################
m = GEKKO(name='tclab-mpc')

# 60 second time horizon, steps of 3 sec
m.time = np.linspace(0,60,21)

# Parameters
U = m.FV(value=10,name='u')
tau = m.FV(value=5,name='tau')
alpha1 = m.FV(value=0.01)   # W / % heater
alpha2 = m.FV(value=0.0075) # W / % heater

Kp = m.Param(value=0.5)
tau = m.Param(value=50.0)
zeta = m.Param(value=1.5)

# Manipulated variables
Q1 = m.MV(value=0)
Q1.STATUS = 1  # use to control temperature
Q1.FSTATUS = 0 # no feedback measurement
Q1.LOWER = 0.0
Q1.UPPER = 100.0
Q1.DMAX = 40.0
Q1.COST = 0.0
Q1.DCOST = 0.0

Q2 = m.MV(value=0)
Q2.STATUS = 1  # use to control temperature
Q2.FSTATUS = 0 # no feedback measurement
Q2.LOWER = 0.0
Q2.UPPER = 100.0
Q2.DMAX = 40.0
Q2.COST = 0.0
Q2.DCOST = 0.0

# Controlled variable
TC1 = m.CV(value=T1[0])
TC1.STATUS = 1     # minimize error with setpoint range
TC1.FSTATUS = 1    # receive measurement
TC1.TR_INIT = 1    # reference trajectory
TC1.TAU = 10       # time constant for response

# Controlled variable
TC2 = m.CV(value=T2[0])
TC2.STATUS = 1     # minimize error with setpoint range
TC2.FSTATUS = 1    # receive measurement
TC2.TR_INIT = 1    # reference trajectory
TC2.TAU = 10       # time constant for response

# State variables
TH1 = m.SV(value=T1[0])
TH2 = m.SV(value=T2[0])

Ta = m.Param(value=23.0+273.15)     # K
mass = m.Param(value=4.0/1000.0)    # kg
Cp = m.Param(value=0.5*1000.0)      # J/kg-K    
A = m.Param(value=10.0/100.0**2)    # Area not between heaters in m^2
As = m.Param(value=2.0/100.0**2)    # Area between heaters in m^2
eps = m.Param(value=0.9)            # Emissivity
sigma = m.Const(5.67e-8)            # Stefan-Boltzmann

# Heater temperatures
T1i = m.Intermediate(TH1+273.15)
T2i = m.Intermediate(TH2+273.15)

# Heat transfer between two heaters
Q_C12 = m.Intermediate(U*As*(T2i-T1i)) # Convective
Q_R12 = m.Intermediate(eps*sigma*As*(T2i**4-T1i**4)) # Radiative

# Semi-fundamental correlations (energy balances)
m.Equation(TH1.dt() == (1.0/(mass*Cp))*(U*A*(Ta-T1i) \
                    + eps * sigma * A * (Ta**4 - T1i**4) \
                    + Q_C12 + Q_R12 \
                    + alpha1*Q1))

m.Equation(TH2.dt() == (1.0/(mass*Cp))*(U*A*(Ta-T2i) \
                    + eps * sigma * A * (Ta**4 - T2i**4) \
                    - Q_C12 - Q_R12 \
                    + alpha2*Q2))

# Empirical correlations (lag equations to emulate conduction)
m.Equation(tau * TC1.dt() == -TC1 + TH1)
m.Equation(tau * TC2.dt() == -TC2 + TH2)

# Global Options
#m.server = 'http://127.0.0.1' # local server, if available
m.options.IMODE   = 6 # MPC
m.options.CV_TYPE = 1 # Objective type
m.options.NODES   = 3 # Collocation nodes
m.options.SOLVER  = 3 # 1=APOPT, 3=IPOPT
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
        sleep_max = 3.0
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
        TC2.MEAS = T2[i]
        # input setpoint with deadband +/- DT
        DT = 0.1
        TC1.SPHI = Tsp1[i] + DT
        TC1.SPLO = Tsp1[i] - DT
        TC2.SPHI = Tsp2[i] + DT
        TC2.SPLO = Tsp2[i] - DT
        # solve MPC
        m.solve(disp=False)    
        # test for successful solution
        if (m.options.APPSTATUS==1):
            # retrieve the first Q value
            Q1s[i] = Q1.NEWVAL
            Q2s[i] = Q2.NEWVAL
        else:
            # not successful, set heater to zero
            Q1s[i] = 0        
            Q2s[i] = 0        
        
        # Write output (0-100)
        a.Q1(Q1s[i])
        a.Q2(Q2s[i])

        # Plot
        plt.clf()
        ax=plt.subplot(3,1,1)
        ax.grid()
        plt.plot(tm[0:i],T1[0:i],'ro',MarkerSize=3,label=r'$T_1$')
        plt.plot(tm[0:i],Tsp1[0:i],'k-',LineWidth=2,label=r'$T_1 Setpoint$')
        plt.ylabel('Temperature (degC)')
        plt.legend(loc='best')
        ax=plt.subplot(3,1,2)
        ax.grid()
        plt.plot(tm[0:i],T2[0:i],'ro',MarkerSize=3,label=r'$T_2$')
        plt.plot(tm[0:i],Tsp2[0:i],'g-',LineWidth=2,label=r'$T_2 Setpoint$')
        plt.ylabel('Temperature (degC)')
        plt.legend(loc='best')
        ax=plt.subplot(3,1,3)
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
