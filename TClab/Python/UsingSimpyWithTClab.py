#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  1 20:58:41 2017

@author: jeff
"""

import pandas as pd
import simpy.rt
from TClab import TClab

df = pd.DataFrame([])
def dataLog(env,df):
    df = df.append([env.now, a.Q1, a.Q2, a.T1, a.T2])
    while True:
        yield env.timeout(1)
        df = df.append([env.now, a.Q1, a.Q2, a.T1, a.T2])

        


a = TClab(simulation=True)
a.Q1 = 100
a.Q2 = 50

env = simpy.rt.RealtimeEnvironment()
env.process(dataLog(env,df))
env.run(until=5)
