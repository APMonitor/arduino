#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  1 23:56:05 2017

@author: jeff
"""

import numpy as np

df = pd.DataFrame(a._log,columns=['Time','var','val'])
df.set_index('Time')

for key in ['Q1','Q2','T1','T2']:
    u = df.loc[df['var'] == key,'val']
    df.loc[u.index,key] = u
    
df.drop('val', inplace=True, axis=1)
df.drop('var', inplace=True, axis=1)
df.set_index('Time',inplace=True)
df = df.groupby(df.index).aggregate(np.mean)
df.fillna(method='ffill',axis=1,inplace=True)

#df['dt'] = df['Time'].diff()
#df.loc[0,'dt'] = 0


#df.loc[(df['dt'] >= 0.1),'dt'] = 1
#df.loc[(df['dt'] < 0.1),'dt'] = 0
#df['dt'] = (df['dt'].cumsum()).astype(int)

#gp = df.groupby('dt')



#df[df['dt'] < 0.1] = 0
#df['dt'] = df['dt'].cumsum()

