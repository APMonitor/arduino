#!/usr/bin/env python
import sys
import serial
import time
from serial.tools import list_ports
from math import ceil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython import display

class TCLabClockError(RuntimeError):
    def __init__(self, message):
        RuntimeError.__init__(self, message)

def clock(tfinal, tstep=1, strict=True):
    start_time = time.time()
    prev_time = start_time
    fuzz = 0.005
    k = 0
    while (prev_time-start_time) <= tfinal  + fuzz:
        if strict and ((prev_time - start_time) > (k*tstep + fuzz)):
            raise TCLabClockError("TCLab failed to keep up with real time.")
        yield round(prev_time - start_time,2)
        if strict:
            tsleep = (k+1)*tstep - (time.time() - start_time) - fuzz
        else:
            tsleep = tstep - (time.time() - prev_time) - fuzz
        if tsleep >= fuzz:
            time.sleep(tsleep)
        prev_time = time.time()
        k += 1
        
class TCLab(object):

    def __init__(self, port=None, baud=9600):
        if (sys.platform == 'darwin') and not port:
            port = '/dev/tty.wchusbserial1410'
        else:
            port = self.findPort()
        print('Opening connection')
        self.sp = serial.Serial(port=port, baudrate=baud, timeout=2)
        self.sp.flushInput()
        self.sp.flushOutput()
        time.sleep(3)
        print('TCLab connected via Arduino on port ' + port)
        self.start()
        
    def findPort(self):
        found = False
        for port in list(list_ports.comports()):
            # Arduino Uno
            if port[2].startswith('USB VID:PID=16D0:0613'):
                port = port[0]
                found = True
            # HDuino
            if port[2].startswith('USB VID:PID=1A86:7523'):
                port = port[0]
                found = True                
        if (not found):
            print('Arduino COM port not found')
            print('Please ensure that the USB cable is connected')
            print('--- Printing Serial Ports ---')            
            for port in list(serial.tools.list_ports.comports()):
                print(port[0] + ' ' + port[1] + ' ' + port[2])
            port = 'COM3'
        return port
    
    def initplot(self,tf):
        # create an empty plot, and keep the line object around
        plt.figure(figsize=(12,6))
        plt.subplot(2,1,1)
        self.line_T1, = plt.plot([],[],lw=2,alpha=0.6)
        self.line_T2, = plt.plot([],[],lw=2,alpha=0.6)
        plt.xlim(0,tf)
        plt.ylim(15,85)
        plt.title('Temperature Control Lab')
        plt.ylabel('deg C')
        plt.xlabel('Seconds')
        plt.legend(['T1','T2'])
        plt.grid()

        plt.subplot(2,1,2)
        self.line_Q1, = plt.step([],[],where='post',lw=2,alpha=0.6)
        self.line_Q2, = plt.step([],[],where='post',lw=2,alpha=0.6)
        plt.xlim(0,tf)
        plt.ylim(-5,105)
        plt.ylabel('mV')
        plt.xlabel('Seconds')
        plt.legend(['Q1','Q2'])
        plt.grid()

        plt.tight_layout()
        
    def updateplot(self):
        tp = time.time() - self.tstart
        self.line_T1.set_xdata(np.append(self.line_T1.get_xdata(),tp))
        self.line_T1.set_ydata(np.append(self.line_T1.get_ydata(),self.T1))
        self.line_T2.set_xdata(np.append(self.line_T2.get_xdata(),tp))
        self.line_T2.set_ydata(np.append(self.line_T2.get_ydata(),self.T2))
        self.line_Q1.set_xdata(np.append(self.line_Q1.get_xdata(),tp))
        self.line_Q1.set_ydata(np.append(self.line_Q1.get_ydata(),self.Q1))
        self.line_Q2.set_xdata(np.append(self.line_Q2.get_xdata(),tp))
        self.line_Q2.set_ydata(np.append(self.line_Q2.get_ydata(),self.Q2))
        display.clear_output(wait=True)
        display.display(plt.gcf())

    def start(self):
        self.tstart = time.time()
        self.tlog = 0
        self.tprev = 0
        self._Q1 = 0
        self._Q2 = 0
        self._log = []
        return self.read('A')

    def stop(self):
        return self.read('X')
    
    @property
    def version(self):
        return self.read('V')
    
    @property
    def T1(self):
        self._T1 = float(self.read('T1'))
        self.updateLog('T1',self._T1)
        return self._T1
    
    @property
    def T2(self):
        self._T2 = float(self.read('T2'))
        self.updateLog('T2',self._T2)
        return self._T2
    
    @property
    def Q1(self):
        return self._Q1
    
    @Q1.setter
    def Q1(self,pwm):
        pwm = max(0,min(255,pwm)) 
        self._Q1 = int(self.write('Q1',pwm))
        self.updateLog('Q1',self._Q1)
    
    @property
    def Q2(self):
        return self._Q2
    
    @Q2.setter
    def Q2(self,pwm):
        pwm = max(0,min(255,pwm)) 
        self._Q2 = int(self.write('Q2',pwm))
        self.updateLog('Q2',self._Q2)
        
    @property
    def log(self):
        df = pd.DataFrame(self._log, columns = ['Time','var','val'])
        for key in ['Q1','Q2','T1','T2']:
            u = df.loc[df['var'] == key,'val']
            df.loc[u.index,key] = u
        df.drop('val', inplace=True, axis=1)
        df.drop('var', inplace=True, axis=1)
        df.set_index('Time',inplace=True)
        df = df.groupby(df.index).aggregate(np.mean)
        df.fillna(method='ffill',inplace=True)
        return df
    
    def updateLog(self,var,val):
        tnow = time.time()-self.tstart
        dt = tnow - self.tlog
        self.tlog = tnow if dt > 0.01 else self.tlog
        self._log.append([self.tlog, var, val])
 
    def plot(self):
        fig, axes = plt.subplots(nrows=2, ncols=1)
        self.log[['Q1','Q2']].plot(grid=True, kind='line', 
                drawstyle='steps-post', ax=axes[0])
        axes[0].set_ylabel('mV')
        self.log[['T1','T2']].plot(grid=True, kind='line', ax=axes[1])
        axes[1].set_ylabel('deg C')
        plt.tight_layout()
    
    def read(self,cmd):
        cmd_str = self.build_cmd_str(cmd,'')
        try:
            self.sp.write(cmd_str.encode())
            self.sp.flush()
        except Exception:
            return None
        return self.sp.readline().decode('UTF-8').replace("\r\n", "")
    
    def write(self,cmd,pwm):       
        cmd_str = self.build_cmd_str(cmd,(pwm,))
        try:
            self.sp.write(cmd_str.encode())
            self.sp.flush()
        except:
            return None
        return self.sp.readline().decode('UTF-8').replace("\r\n", "")
    
    def build_cmd_str(self,cmd, args=None):
        """
        Build a command string that can be sent to the arduino.
    
        Input:
            cmd (str): the command to send to the arduino, must not
                contain a % character
            args (iterable): the arguments to send to the command
        """
        if args:
            args = ' '.join(map(str, args))
        else:
            args = ''
        return "{cmd} {args}\n".format(cmd=cmd, args=args)
        
    def close(self):
        try:
            self.sp.close()
            print('Arduino disconnected successfully')
        except:
            print('Problems disconnecting from Arduino.')
            print('Please unplug and replug Arduino.')
        return True
    