#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 15:40:57 2017

@author: jeff
"""

from tc_lab import TC_Lab
import pandas as pd
import numpy as np
import time

a = TC_Lab()



H = 3

start = time.time()
prev = start
a.Q1 = 100
dt = 10
t = 0
df = [[t,a.T1,a.T2]]p


for k in range(1,H+1):
    t = k*dt
    time.sleep(start+t - prev)
    prev = time.time()
    print(t,a.T1,a.T2)
    df.append([t,a.T1,a.T1])
    
    
    
a.Q1 = 0
    