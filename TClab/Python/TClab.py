#!/usr/bin/env python
import sys
import serial
import time
from serial.tools import list_ports
from math import ceil


class TClab(object):

    def __init__(self, simulation=False, port=None, baud=9600, timeout=0):
        if not(simulation) :
            if (sys.platform == 'darwin') and not port:
                port = '/dev/tty.wchusbserial1410'
            else:
                port = self.findPort()
            print('Opening connection')
            self.sp = serial.Serial(port=port, baudrate=baud, timeout=timeout)
            time.sleep(3)
            print('TClab connected via Arduino on port ' + port)
            self.read = self.readArduino
            self.write = self.writeArduino
        else :
            print('TClab connected via Simulation')
            self.read = self.readSimulation
            self.write = self.writeSimulation
            self.T1sim = 20.0
            self.T2sim = 20.0
            self.tstart = time.time()   
            self.tsim = 0
        self._Q1 = 0
        self._Q2 = 0
        
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
    
    @property
    def version(self):
        return self.read('version')
    
    @property
    def T1(self):
        self._T1 = float(self.read('T1'))
        return self._T1
    
    @property
    def T2(self):
        self._T2 = float(self.read('T2'))
        return self._T2
    
    @property
    def Q1(self):
        return self._Q1
    
    @Q1.setter
    def Q1(self,pwm):
        self._Q1 = int(self.write('Q1',pwm))
    
    @property
    def Q2(self):
        return self._Q2
    
    @Q2.setter
    def Q2(self,pwm):
        self._Q2 = int(self.write('Q2',pwm))
    
    def readArduino(self,cmd):
        cmd_str = cmd
        try:
            self.sp.write(cmd_str.encode())
            self.sp.flush()
        except Exception:
            return None
        return self.sp.readline().decode('UTF-8').replace("\r\n", "")
    
    def writeArduino(self,cmd,pwm):
        pwm = max(0,min(255,pwm))        
        cmd_str = "{cmd} {args}\n".format(cmd=cmd, args=pwm)
        try:
            self.sp.write(cmd_str.encode())
            self.sp.flush()
        except:
            return None
        return self.sp.readline().decode('UTF-8').replace("\r\n", "")
    
    def readSimulation(self,cmd):
        self.updateSimulation()
        return {
            'version': 'TClab Simulation Version 0.1',
            'T1' : "{0:.2f}".format(self.T1sim).encode(),
            'T2' : "{0:.2f}".format(self.T2sim).encode(),
        }[cmd]
    
    def writeSimulation(self,cmd,pwm):
        self.updateSimulation()
        pwm = max(0,min(255,pwm))
        return "{pwm}".format(pwm=pwm).encode()
    
    def updateSimulation(self):
        tprev = self.tsim
        self.tsim = time.time() - self.tstart
        n = ceil((self.tsim - tprev)/0.5)
        dt = (self.tsim - tprev)/n
        for k in range(0,n):
            self.T1sim += 0.01*dt*(self._Q1 - (self.T1sim - 20.0) - 0.2*(self.T2sim - 20.0))
            self.T2sim += 0.01*dt*(self._Q2 - (self.T2sim - 20.0) - 0.2*(self.T1sim - 20.0))
        
    def close(self):
        try:
            self.sp.close()
            print('Arduino disconnected succesfully')
        except:
            print('Problems disconnecting from Arduino.')
            print('Please unplug and replug Arduino.')
        return True
