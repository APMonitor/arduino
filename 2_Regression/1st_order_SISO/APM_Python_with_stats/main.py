from apm import *
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import pandas as pd

# specify s=server and a=application names
s = 'http://byu.apmonitor.com'
a = 'estimate'

# clear previous applicaiton by that name
apm(s,a,'clear all')

# load model and data files
apm_load(s,a,'data.apm')
csv_load(s,a,'data.csv')

# change to dynamic estimation
apm_option(s,a,'nlc.imode',5)
apm_option(s,a,'nlc.ev_type',1)
apm_option(s,a,'nlc.solver',1)

# specify parameters to estimate
apm_info(s,a,'FV','K')
apm_info(s,a,'FV','tau')
apm_option(s,a,'K.status',1)
apm_option(s,a,'tau.status',1)
apm_option(s,a,'K.lower',0.1)
apm_option(s,a,'tau.lower',60)
apm_option(s,a,'K.upper',0.5)
apm_option(s,a,'tau.upper',300)

# specify time varying input(s)
apm_info(s,a,'MV','voltage')

# specify variable(s) to fit to data
apm_info(s,a,'CV','temperature')
apm_option(s,a,'temperature.fstatus',1)
apm_option(s,a,'temperature.meas_gap',4)

# Solve model and return solution
output = apm(s,a,'solve')
print (output)

# retrieve solution
ans = apm_sol(s,a)
obj = apm_tag(s,a,'nlc.objfcnval')

# display results
print ('New Value of K (Gain)           : ' + str(ans['k'][0]))
print ('New Value of Tau (Time Constant): ' + str(ans['tau'][0]))
print ('l1 Norm Objective Function: ' + str(obj))

# open web-viewer
apm_web(s,a)

# load data
data = pd.read_csv('data.csv',delimiter=',')

# plot results
plt.figure()
plt.subplot(211)
plt.plot(ans['time'],ans['voltage'],'g-')
plt.legend(['Voltage'])
plt.ylabel('Voltage (mV)')
plt.subplot(212)
plt.plot(ans['time'],ans['temperature'],'k--')
plt.plot(data['time'],data['temperature'],'r.')
plt.legend(['Predicted Temperature','Measured Temperature'])
plt.ylabel('Temperature (degF)')

# Generate contour plot of SSE ratio vs. Parameters
# design variables at mesh points between the optimal values
k = 0.255487983
tau = 231.4510971
# meshgrid is +/- change in the objective value
i1 = np.arange(k*0.99,k*1.01,k*0.0005)
i2 = np.arange(tau*0.98,tau*1.02,tau*0.0005)
k_grid, tau_grid = np.meshgrid(i1, i2)

dt = 1 # delta time step
v0 = data['voltage'][0] # initial voltage
t0 = data['temperature'][0] # initial temperature
n = 851 # number of measurements
p = 2 # number of parameters

c = np.exp(-dt/tau_grid)
(s1,s2) = c.shape
t = t0 * np.ones([s1,s2])
sse = np.zeros([s1,s2])
for i in range(1,n):
    t = (t-t0) * c + data['voltage'][i-1] * k_grid * (1.0 - c) + t0
    sse = sse + (t-data['temperature'][i])**2

# normalize to the best solution
best_sse = np.min(np.min(sse))
fsse = (sse - best_sse) / best_sse

# compute f-statistic for the f-test
alpha = 0.05 # alpha, confidence (alpha = 0.05 is 95% confidence)
fstat = scipy.stats.f.isf(alpha,p,(n-p))
flim = fstat * p / (n-p)
obj_lim = flim * best_sse + best_sse

print ('f-test limit for SSE fractional deviation: ' + str(flim))

# Create a contour plot
plt.figure()
CS = plt.contour(k_grid,tau_grid,sse)
plt.clabel(CS, inline=1, fontsize=10)
plt.title('Contour Plot')
plt.xlabel('Gain (K)')
plt.ylabel('Time Constant (tau)')
# solid line to show confidence region
CS = plt.contour(k_grid,tau_grid,sse,[obj_lim],colors='b',linewidths=[2.0])
plt.clabel(CS, inline=1, fontsize=10)

# Save the figure as a PNG
plt.savefig('contour.png')

plt.show()

