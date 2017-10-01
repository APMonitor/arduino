#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 14:18:34 2017

@author: jeff
"""

from TClab import TClab
import time

# Connect to Arduino
a = TClab()

# Get Version
print(a.version)

# Read temperatures
print("Temperature 1: = {0:0.2f} C".format(a.T1))
print("Temperature 2: = {0:0.2f} C".format(a.T2))

# Write Voltages
print("\n Set Heaters to 100 mV")
a.Q1 = 100
a.Q2 = 100
for i in range(0,65,5):
    sfmt = "{0:3d} sec: T1 = {1:0.2f} C  T2 = {2:0.2f} C"
    print(sfmt.format(i, a.T1, a.T2))
    time.sleep(5)

print("\n Set Heaters to 0 mV")
a.Q1 = 0
a.Q2 = 0
for i in range(65,125,5):
    sfmt = "Time {0:3d} : T1 = {1:0.2f} C  T2 = {2:0.2f} C"
    print(sfmt.format(i, a.T1, a.T2))
    time.sleep(5)

#a.close()