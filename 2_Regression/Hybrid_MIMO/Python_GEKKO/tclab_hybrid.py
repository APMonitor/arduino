import numpy as np
import time
import matplotlib.pyplot as plt
import random
import pandas as pd
# get gekko package with:
#   pip install gekko
from gekko import GEKKO

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
m = GEKKO(name='tclab-estimation')
#m.server = 'http://127.0.0.1' # if local server is installed

# 60 second time horizon, 150 steps
m.time = tm

# Parameters to Estimate
U = m.FV(value=10)
U.STATUS = 1
U.FSTATUS = 0 # no measurements
U.LOWER = 2
U.UPPER = 20

tau = m.FV(value=5)
tau.STATUS = 1
tau.FSTATUS = 0 # no measurements
tau.LOWER = 2
tau.UPPER = 20

alpha1 = m.FV(value=0.01)   # W / % heater
alpha1.STATUS = 1
alpha1.FSTATUS = 0 # no measurements
alpha1.LOWER = 0.003
alpha1.UPPER = 0.03

alpha2 = m.FV(value=0.0075) # W / % heater
alpha2.STATUS = 1
alpha2.FSTATUS = 0 # no measurements
alpha2.LOWER = 0.002
alpha2.UPPER = 0.02

Ta = m.FV(value=18.0)    # K
Ta.STATUS = 1
Ta.FSTATUS = 0 # no measurements
Ta.LOWER = 15.0
Ta.UPPER = 25.0

# Measured inputs
Q1 = m.MV(value=Q1s)
Q1.STATUS = 0  # don't estimate
Q1.FSTATUS = 1 # receive measurement

Q2 = m.MV(value=Q2s)
Q2.STATUS = 0  # don't estimate
Q2.FSTATUS = 1 # receive measurement

# State variables
TH1 = m.SV(value=T1s)
TH2 = m.SV(value=T2s)

# Measurements for model alignment
TC1 = m.CV(value=T1s)
TC1.STATUS = 1     # minimize error between simulation and measurement
TC1.FSTATUS = 1    # receive measurement
TC1.MEAS_GAP = 0.1 # measurement deadband gap
TC1.LOWER = 0
TC1.UPPER = 200

TC2 = m.CV(value=T2s)
TC2.STATUS = 1     # minimize error between simulation and measurement
TC2.FSTATUS = 1    # receive measurement
TC2.MEAS_GAP = 0.1 # measurement deadband gap
TC2.LOWER = 0
TC2.UPPER = 200

mass = m.Param(value=4.0/1000.0)    # kg
Cp = m.Param(value=0.5*1000.0)      # J/kg-K    
A = m.Param(value=10.0/100.0**2)    # Area not between heaters in m^2
As = m.Param(value=2.0/100.0**2)    # Area between heaters in m^2
eps = m.Param(value=0.9)            # Emissivity
sigma = m.Const(5.67e-8)            # Stefan-Boltzmann

# Heater temperatures
T1 = m.Intermediate(TH1+273.15)
T2 = m.Intermediate(TH2+273.15)
TaK = m.Intermediate(Ta+273.15)

# Heat transfer between two heaters
Q_C12 = m.Intermediate(U*As*(T2-T1)) # Convective
Q_R12 = m.Intermediate(eps*sigma*As*(T2**4-T1**4)) # Radiative

# Semi-fundamental correlations (energy balances)
m.Equation(TH1.dt() == (1.0/(mass*Cp))*(U*A*(TaK-T1) \
                    + eps * sigma * A * (TaK**4 - T1**4) \
                    + Q_C12 + Q_R12 \
                    + alpha1*Q1))

m.Equation(TH2.dt() == (1.0/(mass*Cp))*(U*A*(TaK-T2) \
                    + eps * sigma * A * (TaK**4 - T2**4) \
                    - Q_C12 - Q_R12 \
                    + alpha2*Q2))

# Empirical correlations (lag equations to emulate conduction)
m.Equation(tau * TC1.dt() == -TC1 + TH1)
m.Equation(tau * TC2.dt() == -TC2 + TH2)

# Global Options
m.options.IMODE   = 5 # MHE
m.options.EV_TYPE = 2 # Objective type
m.options.NODES   = 3 # Collocation nodes
m.options.SOLVER  = 3 # IPOPT
##################################################################

# Predict Parameters and Temperatures with MHE
# use remote=False for local solve
m.solve(remote=True) 

print('U: ' + str(U.NEWVAL))
print('tau: ' + str(tau.NEWVAL))
print('alpha1: ' + str(alpha1.NEWVAL))
print('alpha2: ' + str(alpha2.NEWVAL))
print('Ta: ' + str(Ta.NEWVAL))

# Create plot
plt.figure(figsize=(10,7))
ax=plt.subplot(2,1,1)
ax.grid()
plt.plot(tm,T1s,'ro',label=r'$T_1$ measured')
plt.plot(tm,TC1,'k-',label=r'$T_1$ predicted')
plt.plot(tm,T2s,'bx',label=r'$T_2$ measured')
plt.plot(tm,TC2,'k--',label=r'$T_2$ predicted')
plt.ylabel('Temperature (degC)')
plt.legend(loc=2)
ax=plt.subplot(2,1,2)
ax.grid()
plt.plot(tm,Q1s,'r-',label=r'$Q_1$')
plt.plot(tm,Q2s,'b:',label=r'$Q_2$')
plt.ylabel('Heaters')
plt.xlabel('Time (sec)')
plt.legend(loc='best')
plt.savefig('tclab_estimation.png')
plt.show()
