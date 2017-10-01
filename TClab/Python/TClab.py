#!/usr/bin/env python
import sys
import serial
import time
from serial.tools import list_ports


class TClab(object):

    def __init__(self, baud=9600, port=None, timeout=0):
        if (sys.platform == 'darwin') and not port:
            port = '/dev/tty.wchusbserial1410'
        else:
            port = self.findPort()
        print('Opening connection')
        self.sp = serial.Serial(port=port, baudrate=baud, timeout=timeout)
        time.sleep(3)
        print('Arduino connected on port ' + port)
        self.Q1 = 0
        self.Q2 = 0
        
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
        return self.readArduino('version')
    
    @property
    def T1(self):
        degC = self.readArduino('T1')
        return float(degC) if degC else 0
    
    @property
    def T2(self):
        degC = self.readArduino('T2')
        return float(degC) if degC else 0
    
    @property
    def Q1(self):
        return self._Q1
    
    @Q1.setter
    def Q1(self,pwm):
        self._Q1 = int(self.writeArduino('Q1',pwm))
    
    @property
    def Q2(self):
        return self._Q2
    
    @Q2.setter
    def Q2(self,pwm):
        self._Q2 = int(self.writeArduino('Q2',pwm))
    
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
        
    def close(self):
        try:
            self.sp.close()
            print('Arduino disconnected succesfully')
        except:
            print('Problems disconnecting from Arduino.')
            print('Please unplug and replug Arduino.')
        return True

