#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to test basic functions of TClab and verify the firmware
is functioning correctly. 

Created on Fri Sep 29 14:18:34 2017

@author: jeff
"""

from TClab import TClab
import time

# Connect to Arduino
#a = TClab(simulation=True)
a = TClab()

# Get Version
print(a.version)

# Read temperatures
print()
print("Temperature 1: = {0:0.2f} C".format(a.T1))
print("Temperature 2: = {0:0.2f} C".format(a.T2))

# Write Voltages
a.Q1 = 100
a.Q2 =  50
print()
print("Set Heater 1 to {0:d} mV".format(a.Q1))
print("Set Heater 2 to {0:d} mV".format(a.Q2))
sfmt = "   {0:3d} sec:   T1 = {1:0.2f} C    T2 = {2:0.2f} C"
for i in range(0,65,5):
    print(sfmt.format(i, a.T1, a.T2), flush=True)
    time.sleep(5)

a.Q1 = 0
a.Q2 = 0
print()
print("Set Heater 1 to {0:d} mV".format(a.Q1))
print("Set Heater 2 to {0:d} mV".format(a.Q2))
for i in range(65,125,5):
    print(sfmt.format(i, a.T1, a.T2), flush=True)
    time.sleep(5)
    
a.plot()

#a.close()