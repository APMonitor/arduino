# -*- coding: utf-8 -*-

from arduino import Arduino
import numpy as np
import time

successful = 1

# Connect to Arduino
try:
    a = Arduino()
except:
    successful = 0
    print('Could not connect to Arduino')
