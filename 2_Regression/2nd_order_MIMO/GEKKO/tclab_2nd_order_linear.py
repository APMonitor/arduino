import numpy as np
import time
import matplotlib.pyplot as plt
import random
# get gekko package with:
#   pip install gekko
from gekko import GEKKO
import pandas as pd

# import data
data = pd.read_csv('data.txt')
tm = data['Time (sec)'].values
Q1s = data[' Heater 1'].values
Q2s = data[' Heater 2'].values
T1s = data[' Temperature 1'].values
T2s = data[' Temperature 2'].values

#########################################################
# Initialize Model as Estimator
#########################################################
m = GEKKO(name='tclab-mhe')
#m.server = 'http://127.0.0.1' # if local server is installed

# 120 second time horizon, 40 steps
m.time = tm

# Parameters to Estimate
K1 = m.FV(value=0.5)
K1.STATUS = 1
K1.FSTATUS = 0
K1.LOWER = 0.1
K1.UPPER = 1.0

K2 = m.FV(value=0.3)
K2.STATUS = 1
K2.FSTATUS = 0
K2.LOWER = 0.1
K2.UPPER = 1.0

K3 = m.FV(value=0.1)
K3.STATUS = 1
K3.FSTATUS = 0
K3.LOWER = 0.0001
K3.UPPER = 1.0

tau12 = m.FV(value=150)
tau12.STATUS = 1
tau12.FSTATUS = 0
tau12.LOWER = 50.0
tau12.UPPER = 250

tau3 = m.FV(value=15)
tau3.STATUS = 0
tau3.FSTATUS = 0
tau3.LOWER = 10
tau3.UPPER = 20

# Measured inputs
Q1 = m.MV(value=0)
Q1.FSTATUS = 1 # measured
Q1.value = Q1s

Q2 = m.MV(value=0)
Q2.FSTATUS = 1 # measured
Q2.value = Q2s

# Ambient temperature
Ta = m.Param(value=23.0) # degC

# State variables
TH1 = m.SV(value=T1s[0])
TH2 = m.SV(value=T2s[0])

# Measurements for model alignment
TC1 = m.CV(value=T1s)
TC1.STATUS = 1     # minimize error between simulation and measurement
TC1.FSTATUS = 1    # receive measurement
TC1.MEAS_GAP = 0.1 # measurement deadband gap

TC2 = m.CV(value=T1s[0])
TC2.STATUS = 1     # minimize error between simulation and measurement
TC2.FSTATUS = 1    # receive measurement
TC2.MEAS_GAP = 0.1 # measurement deadband gap
TC2.value = T2s

# Heat transfer between two heaters
DT = m.Intermediate(TH2-TH1)

# Empirical correlations
m.Equation(tau12 * TH1.dt() + (TH1-Ta) == K1*Q1 + K3*DT)
m.Equation(tau12 * TH2.dt() + (TH2-Ta) == K2*Q2 - K3*DT)
m.Equation(tau3 * TC1.dt()  + TC1 == TH1)
m.Equation(tau3 * TC2.dt()  + TC2 == TH2)

# Global Options
m.options.IMODE   = 5 # MHE
m.options.EV_TYPE = 2 # Objective type
m.options.NODES   = 3 # Collocation nodes
m.options.SOLVER  = 3 # IPOPT
m.options.COLDSTART = 0 # COLDSTART on first cycle

# Predict Parameters and Temperatures
# use remote=False for local solve
m.solve() 

# Create plot
plt.figure(figsize=(10,7))

ax=plt.subplot(2,1,1)
ax.grid()
plt.plot(tm,T1s,'ro',label=r'$T_1$ measured')
plt.plot(tm,TC1.value,'k-',label=r'$T_1$ predicted')
plt.plot(tm,T2s,'bx',label=r'$T_2$ measured')
plt.plot(tm,TC2.value,'k--',label=r'$T_2$ predicted')
plt.ylabel('Temperature (degC)')
plt.legend(loc=2)
ax=plt.subplot(2,1,2)
ax.grid()
plt.plot(tm,Q1s,'r-',label=r'$Q_1$')
plt.plot(tm,Q2s,'b:',label=r'$Q_2$')
plt.ylabel('Heaters')
plt.xlabel('Time (sec)')
plt.legend(loc='best')

# Print optimal values
print('K1: ' + str(K1.newval))
print('K2: ' + str(K2.newval))
print('K3: ' + str(K3.newval))
print('tau12: ' + str(tau12.newval))
print('tau3: ' + str(tau3.newval))

# Save figure
plt.savefig('tclab_estimation.png')
plt.show()
        
