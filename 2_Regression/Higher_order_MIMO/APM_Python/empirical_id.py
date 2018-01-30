import numpy as np
import matplotlib.pyplot as plt
from apm import *

######################################################
# Configuration
######################################################
# number of terms
ny = 3 # output coefficients
nu = 3 # input coefficients
# number of inputs
ni = 2
# number of outputs
no = 2
# load data and parse into columns
data = np.loadtxt('data_no_headers.csv',delimiter=',')
######################################################

# generate time-series model
ypred = sysid(data,ni,nu,ny)

# plot results
plt.figure(1)
plt.subplot(2,1,1)
plt.plot(data[:,0],ypred[:,0],'r-',LineWidth=2)
plt.plot(data[:,0],data[:,3],'b--',LineWidth=2)
plt.plot(data[:,0],ypred[:,1],'k-',LineWidth=2)
plt.plot(data[:,0],data[:,4],'g:',LineWidth=2)
plt.legend(['Predicted 1','Measured 1',\
            'Predicted 2','Measured 2'],loc='best')
plt.ylabel('Temp (degC)')

plt.subplot(2,1,2)
plt.plot(data[:,0],data[:,1],'r-',LineWidth=2)
plt.plot(data[:,0],data[:,2],'b--',LineWidth=2)
plt.legend(['Heater 1','Heater 2'],loc='best')
plt.ylabel('Heater')
plt.show()
