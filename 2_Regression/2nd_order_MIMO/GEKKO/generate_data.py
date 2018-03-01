import numpy as np
import time
import matplotlib.pyplot as plt
import random
#   pip install tclab
from tclab import TCLab

# save txt file
def save_txt(t,Q1,Q2,T1,T2):
    data = np.vstack((t,Q1,Q2,T1,T2))  # vertical stack
    data = data.T                 # transpose data
    top = 'Time (sec), Heater 1, Heater 2, ' \
        + 'Temperature 1, Temperature 2' 
    np.savetxt('data.txt',data,delimiter=',',header=top,comments='')

# Connect to Arduino
a = TCLab()

# Final time
tf = 10 # min
# number of data points (every 3 seconds)
n = tf * 20 + 1

# Configure heater levels
# Percent Heater (0-100%)
Q1s = np.zeros(n)
Q2s = np.zeros(n)
# Heater random steps every 50 sec
# Alternate steps by Q1 and Q2
#  with rapid, random changes every 10 cycles
for i in range(1,n):
    if i%20==0:
        Q1s[i:i+20] = random.random() * 100.0
    if (i+10)%20==0:
        Q2s[i:i+20] = random.random() * 100.0

# heater 2 initially off
Q2s[0:50] = 0.0
# heater 1 off at end (last 50 cycles)
Q1s[-50:-1] = 0.0
        
# Record initial temperatures (degC)
T1m = a.T1 * np.ones(n)
T2m = a.T2 * np.ones(n)

##################################################################
# Create plot
plt.figure(figsize=(10,7))
plt.ion()
plt.show()

# Main Loop
start_time = time.time()
prev_time = start_time
tm = np.zeros(n)

try:
    for i in range(1,n):
        # Sleep time
        sleep_max = 3.0
        sleep = sleep_max - (time.time() - prev_time)
        if sleep>=0.01:
            time.sleep(sleep-0.01)
        else:
            time.sleep(0.01)

        # Record time and change in time
        t = time.time()
        dt = t - prev_time
        prev_time = t
        tm[i] = t - start_time

        # Read temperatures in Celsius 
        T1m[i] = a.T1
        T2m[i] = a.T2
                
        # Write new heater values (0-100)
        a.Q1(Q1s[i])
        a.Q2(Q2s[i])

        # Plot
        plt.clf()
        ax=plt.subplot(2,1,1)
        ax.grid()
        plt.plot(tm[0:i],T1m[0:i],'ro',label=r'$T_1$ measured')
        plt.plot(tm[0:i],T2m[0:i],'bx',label=r'$T_2$ measured')
        plt.ylabel('Temperature (degC)')
        plt.legend(loc=2)
        ax=plt.subplot(2,1,2)
        ax.grid()
        plt.plot(tm[0:i],Q1s[0:i],'r-',label=r'$Q_1$')
        plt.plot(tm[0:i],Q2s[0:i],'b:',label=r'$Q_2$')
        plt.ylabel('Heaters')
        plt.xlabel('Time (sec)')
        plt.legend(loc='best')
        plt.draw()
        plt.pause(0.05)

    # Turn off heaters
    a.Q1(0)
    a.Q2(0)
    save_txt(tm,Q1s,Q2s,T1m,T2m)
    # Save figure
    plt.savefig('tclab_data.png')
    
# Allow user to end loop with Ctrl-C           
except KeyboardInterrupt:
    # Disconnect from Arduino
    a.Q1(0)
    a.Q2(0)
    print('Shutting down')
    a.close()
    plt.savefig('tclab_data.png')
    
# Make sure serial connection still closes when there's an error
except:           
    # Disconnect from Arduino
    a.Q1(0)
    a.Q2(0)
    print('Error: Shutting down')
    a.close()
    plt.savefig('tclab_data.png')
    raise
