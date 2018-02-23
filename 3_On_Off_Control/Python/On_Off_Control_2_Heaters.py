import numpy as np
from tclab import TCLab
import time
import matplotlib.pyplot as plt

a = TCLab()

# total time points
n = 10 * 60 + 1 # min in sec

# turn on LED
a.LED(100)

# store temperatures for plotting
T1s = np.ones(n) * a.T2
T2s = np.ones(n) * a.T1
T1sp = np.ones(n) * 25.0
T2sp = np.ones(n) * 25.0
# store heater values
Q1s = np.ones(n)
Q2s = np.ones(n)
# store time
tm = np.zeros(n)

# set point changes
T1sp[5:] = 40.0
T1sp[300:] = 30.0
T2sp[150:] = 30.0
T2sp[450:] = 35.0

# Create plot
plt.figure()
plt.ion()
plt.show()

for i in range(1,n):
    time.sleep(0.9)
    tm[i] = time.clock()

    # read temperature
    T1s[i] = a.T1
    T2s[i] = a.T2

    # apply ON/OFF controller
    # heater 1
    if T1s[i] < T1sp[i]:
        Q1s[i] = 100.0
    else:
        Q1s[i] = 0.0
    # heater 2
    if T2s[i] < T2sp[i]:
        Q2s[i] = 100.0
    else:
        Q2s[i] = 0.0

    a.Q1(Q1s[i])
    a.Q2(Q2s[i])

    # Plot
    plt.clf()
    ax=plt.subplot(3,1,1)
    ax.grid()
    plt.plot(tm[0:i],T1s[0:i],'ro',MarkerSize=3,label=r'$T_1$')
    plt.plot(tm[0:i],T1sp[0:i],'k-',LineWidth=2,label=r'$T_1 Setpoint$')
    plt.ylabel('Temperature (degC)')
    plt.legend(loc='best')
    ax=plt.subplot(3,1,2)
    ax.grid()
    plt.plot(tm[0:i],T2s[0:i],'ro',MarkerSize=3,label=r'$T_2$')
    plt.plot(tm[0:i],T2sp[0:i],'g-',LineWidth=2,label=r'$T_2 Setpoint$')
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

# turn off heaters
a.Q1(0)
a.Q2(0)
# turn off LED
a.LED(0)
