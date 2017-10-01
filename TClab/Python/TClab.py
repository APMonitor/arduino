#!/usr/bin/env python
import sys
import serial
import time
from serial.tools import list_ports


class TClab(object):

    def __init__(self, baud=9600, port=None, timeout=2):
        if (sys.platform == 'darwin') and not port:
            port = '/dev/tty.wchusbserial1410'
        else:
            port = self.findPort()
        print('Opening connection')
        self.sp = serial.Serial(port=port, baudrate=baud, timeout=timeout)
        time.sleep(3)
        print('Arduino connected on port '+port)
        self.Q1 = 0
        self.Q2 = 0
        self.LED = 0
        
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
        self.writeArduino('Q1',pwm)
        self._Q1 = pwm
        
    def setQ1(self,pwm):
        self.writeArduino('Q1',pwm)
        self._Q1 = pwm
    
    @property
    def Q2(self):
        return self._Q2
    
    @Q2.setter
    def Q2(self,pwm):
        self.writeArduino('Q2',pwm)
        self._Q2 = pwm
        
    def setQ2(self,pwm):
        self.writeArduino('Q2',pwm)
        self._Q2 = pwm
        
    @property
    def LED(self):
        return self._LED
    
    @LED.setter
    def LED(self,pwm):
        self.writeArduino('LED1',pwm)
        self._LED = pwm

    def setLED(self,pwm):
        self.writeArduino('LED1',pwm)
        self._LED = pwm
    
    def readArduino(self,cmd):
        cmd_str = self.build_cmd_str(cmd,('',))
        try:
            self.sp.write(cmd_str.encode())
            self.sp.flush()
        except Exception:
            return None
        return self.sp.readline().decode('UTF-8').replace("\r\n", "")
    
    def writeArduino(self,cmd,pwm):
        pwm = max(0,min(255,pwm))        
        cmd_str = self.build_cmd_str(cmd,(pwm,))
        try:
            self.sp.write(cmd_str.encode())
            self.sp.flush()
        except:
            pass
        
    def close(self):
        try:
            self.sr.close()
            print('Arduino disconnected succesfully')
        except:
            print('Problems disconnecting from Arduino.')
            print('Please unplug and replug Arduino.')
        return True

    def build_cmd_str(self,cmd, args=None):
        """
        Build a command string that can be sent to the arduino.
    
        Input:
            cmd (str): the command to send to the arduino, must not
                contain a % character
            args (iterable): the arguments to send to the command
    
        @TODO: a strategy is needed to escape % characters in the args
        """
        if args:
            args = ' '.join(map(str, args))
        else:
            args = ''
        return "{cmd} {args}\n".format(cmd=cmd, args=args)
