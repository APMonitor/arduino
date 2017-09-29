#!/usr/bin/env python
import subprocess
import sys
try:
    import serial
    import pyqtgraph as pg
except:
    print('Attempting to install missing packages.  Please Wait')
    subprocess.call('pip install -y pyserial pyqtgraph', shell=True)
    import serial
    import pyqtgraph as pg
    print('**********************************************************')
    print('Done installing new packages, please restart Python kernel')
    print('**********************************************************')
    sys.exit()
import time
from serial.tools import list_ports
from serial import SerialException
import pandas as pd
import numpy as np

class Arduino(object):

    def __init__(self, baud=9600, port=None, timeout=2, sr=None):
        # Connect to serial port
        port = self.findPort()
        print('Opening connection')
        self.s = serial.Serial(port=port, baudrate=115200, timeout=2)
        time.sleep(3)
        self.sr = self.s
        self.tempInPin = 0
        self.voltOutPin = 3
        self.tempInPin2 = 2
        self.voltOutPin2 = 5
        print('Arduino connected on port '+port)
        #print('Current configuration is:')
        #print('Read temperature 1 on analog pin '+ str(self.tempInPin))
        #print('Write voltage 1 on digital pin '+ str(self.voltOutPin))
        #print('Read temperature 2 on analog pin '+ str(self.tempInPin2))
        #print('Write voltage 2 on digital pin '+ str(self.voltOutPin2))
        
    def findPort(self):
        found = False
        for port in list(serial.tools.list_ports.comports()):
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
        
    def initPlots(self):
        # Initialize data array
        self.data = np.array([[0, 0, self.readTemp(), 0, 0, self.readTemp2(), 0]])        
        
        # Create figure window
        self.win = pg.GraphicsWindow()
        self.win.resize(1000,600)
        self.win.setWindowTitle('Arduino Temperature Control Lab')
        pg.setConfigOptions(antialias=True)
        
        # Create temperature 1 plot
        self.plt = self.win.addPlot(title="Temperature vs Time",row=1,col=1)
        self.plt.setRange(yRange=[280,380])
        yaxis = self.plt.getAxis('left')
        labelStyle = {'color': '#FFF', 'font-size': '14pt'}
        yaxis.setLabel('Temperature','K', **labelStyle)
        yaxis.setGrid(150)
        
        # Create voltage 1 plot
        self.plt2 = self.win.addPlot(row=2,col=1)
        self.plt2.setRange(yRange=[0,255])
        xaxis = self.plt2.getAxis('bottom')
        xaxis.setLabel('Time','s', **labelStyle)
        yaxis2 = self.plt2.getAxis('left')
        yaxis2.setLabel('Voltage','mV', **labelStyle)
        yaxis2.setGrid(100)

        # Create temperature 2 plot
        self.plt3 = self.win.addPlot(title="Temperature vs Time",row=3,col=1)
        self.plt3.setRange(yRange=[280,380])
        yaxis3 = self.plt3.getAxis('left')
        labelStyle = {'color': '#FFF', 'font-size': '14pt'}
        yaxis3.setLabel('Temperature','K', **labelStyle)
        yaxis3.setGrid(150)
        
        # Create voltage 2 plot
        self.plt4 = self.win.addPlot(row=4,col=1)
        self.plt4.setRange(yRange=[0,255])
        xaxis = self.plt4.getAxis('bottom')
        xaxis.setLabel('Time','s', **labelStyle)
        yaxis4 = self.plt4.getAxis('left')
        yaxis4.setLabel('Voltage','mV', **labelStyle)
        yaxis4.setGrid(100)
        
        return True
        
    def addData(self,newData):
        self.data = np.r_[self.data,newData]
        return True
    
    def updatePlots(self):
        self.plt.plot(self.data[-300:,0],self.data[-300:,2], pen=pg.mkPen('r',width=3),clear=True)
        self.plt2.plot(self.data[-300:,0],self.data[-300:,1], pen=pg.mkPen('b',width=3),clear=True)
        self.plt3.plot(self.data[-300:,0],self.data[-300:,5], pen=pg.mkPen('r',width=3),clear=True)
        self.plt4.plot(self.data[-300:,0],self.data[-300:,4], pen=pg.mkPen('b',width=3),clear=True)
        self.plt.addLine(y=self.data[-1,3])
        pg.QtGui.QApplication.processEvents()
        return True
        
    def saveData(self):
        df = pd.DataFrame(self.data)
        C = ['Time (s)', 'V1 (mV)', 'T1 (K)', 'T1_SP (K)', 'V2 (mV)', 'T2 (K)', 'T2_SP (K)']
        df.to_excel("data.xls", header=C, index=False)
        print('Data Saved to Output folder')
        return True
        
    def movingaverage(self,interval, window_size):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')
        
    def readTemp(self):
        val = self.analogRead(self.tempInPin)
        voltage = float(val) * (3300.0/1024.0)
        degC = (voltage - 500.0)/10.0
        degK = degC + 273.15
        return degK

    def readTempC(self):
        return self.readTemp() - 273.15

    def readTempF(self):
        return self.readTemp() * 9.0 / 5.0 - 459.67
        
    def readTemp2(self):
        val = self.analogRead(self.tempInPin2)
        voltage = float(val) * (3300.0/1024.0)
        degC = (voltage - 500.0)/10.0
        degK = degC + 273.15
        return degK
        
    def readTempC2(self):
        return self.readTemp2() - 273.15

    def readTempF2(self):
        return self.readTemp2() * 9.0 / 5.0 - 459.67

    def writeVoltage(self,mV):
        self.analogWrite(self.voltOutPin,mV)
        return True
        
    def writeVoltage2(self,mV):
        self.analogWrite(self.voltOutPin2,mV)
        return True
        
    def led(self,level):
        # level = 0-100%
        level = max(0,min(100,level))
        out = int(level / 2.0)
        self.analogWrite(9,out)
        return True
        
    def close(self):
        try:
            self.s.close()
            print('Arduino disconnected succesfully')
        except:
            print('Problems disconnecting from Arduino.  Please unplug and replug Arduino.')
        return True

    def version(self):
        return self.get_version(self.sr)

    def digitalWrite(self, pin, val):
        """
        Sends digitalWrite command
        to digital pin on Arduino
        -------------
        inputs:
           pin : digital pin number
           val : either "HIGH" or "LOW"
        """
        if val == "LOW":
            pin_ = -pin
        else:
            pin_ = pin
        cmd_str = self.build_cmd_str("dw", (pin_,))
        try:
            self.sr.write(cmd_str.encode())
            self.sr.flush()
        except:
            pass

    def analogWrite(self, pin, val):
        """
        Sends analogWrite pwm command
        to pin on Arduino
        -------------
        inputs:
           pin : pin number
           val : integer 0 (off) to 255 (always on)
        """
        if val > 255:
            val = 255
        elif val < 0:
            val = 0
        cmd_str = self.build_cmd_str("aw", (pin, val))
        try:
            self.sr.write(cmd_str.encode())
            self.sr.flush()
        except:
            pass

    def analogRead(self, pin):
        """
        Returns the value of a specified
        analog pin.
        inputs:
           pin : analog pin number for measurement
        returns:
           value: integer from 1 to 1023
        """
        cmd_str = self.build_cmd_str("ar", (pin,))
        try:
            self.sr.write(cmd_str.encode())
            self.sr.flush()
        except:
            pass
        rd = self.sr.readline().decode("utf-8").replace("\r\n", "")
        try:
            return int(rd)
        except:
            return 0

    def pinMode(self, pin, val):
        """
        Sets I/O mode of pin
        inputs:
           pin: pin number to toggle
           val: "INPUT" or "OUTPUT"
        """
        if val == "INPUT":
            pin_ = -pin
        else:
            pin_ = pin
        cmd_str = self.build_cmd_str("pm", (pin_,))
        try:
            self.sr.write(cmd_str.encode())
            self.sr.flush()
        except:
            pass

    def pulseIn(self, pin, val):
        """
        Reads a pulse from a pin

        inputs:
           pin: pin number for pulse measurement
        returns:
           duration : pulse length measurement
        """
        if val == "LOW":
            pin_ = -pin
        else:
            pin_ = pin
        cmd_str = self.build_cmd_str("pi", (pin_,))
        try:
            self.sr.write(cmd_str.encode())
            self.sr.flush()
        except:
            pass
        rd = self.sr.readline().decode("utf-8").replace("\r\n", "")
        try:
            return float(rd)
        except:
            return -1

    def pulseIn_set(self, pin, val, numTrials=5):
        """
        Sets a digital pin value, then reads the response
        as a pulse width.
        Useful for some ultrasonic rangefinders, etc.

        inputs:
           pin: pin number for pulse measurement
           val: "HIGH" or "LOW". Pulse is measured
                when this state is detected
           numTrials: number of trials (for an average)
        returns:
           duration : an average of pulse length measurements

        This method will automatically toggle
        I/O modes on the pin and precondition the
        measurment with a clean LOW/HIGH pulse.
        Arduino.pulseIn_set(pin,"HIGH") is
        equivalent to the Arduino sketch code:

        pinMode(pin, OUTPUT);
        digitalWrite(pin, LOW);
        delayMicroseconds(2);
        digitalWrite(pin, HIGH);
        delayMicroseconds(5);
        digitalWrite(pin, LOW);
        pinMode(pin, INPUT);
        long duration = pulseIn(pin, HIGH);
        """
        if val == "LOW":
            pin_ = -pin
        else:
            pin_ = pin
        cmd_str = self.build_cmd_str("ps", (pin_,))
        durations = []
        for s in range(numTrials):
            try:
                self.sr.write(cmd_str.encode())
                self.sr.flush()
            except:
                pass
            rd = self.sr.readline().decode("utf-8").replace("\r\n", "")
            if rd.isdigit():
                if (int(rd) > 1):
                    durations.append(int(rd))
        if len(durations) > 0:
            duration = int(sum(durations)) / int(len(durations))
        else:
            duration = None

        try:
            return float(duration)
        except:
            return -1

    def digitalRead(self, pin):
        """
        Returns the value of a specified
        digital pin.
        inputs:
           pin : digital pin number for measurement
        returns:
           value: 0 for "LOW", 1 for "HIGH"
        """
        cmd_str = self.build_cmd_str("dr", (pin,))
        try:
            self.sr.write(cmd_str.encode())
            self.sr.flush()
        except:
            pass
        rd = self.sr.readline().decode("utf-8").replace("\r\n", "")
        try:
            return int(rd)
        except:
            return 0

    def Melody(self, pin, melody, durations):
        """
        Plays a melody.
        inputs:
            pin: digital pin number for playback
            melody: list of tones
            durations: list of duration (4=quarter note, 8=eighth note, etc.)
        length of melody should be of same
        length as length of duration

        Melodies of the following length, can cause trouble
        when playing it multiple times.
            board.Melody(9,["C4","G3","G3","A3","G3",0,"B3","C4"],
                                                [4,8,8,4,4,4,4,4])
        Playing short melodies (1 or 2 tones) didn't cause
        trouble during testing
        """
        NOTES = dict(
            B0=31, C1=33, CS1=35, D1=37, DS1=39, E1=41, F1=44, FS1=46, G1=49,
            GS1=52, A1=55, AS1=58, B1=62, C2=65, CS2=69, D2=73, DS2=78, E2=82,
            F2=87, FS2=93, G2=98, GS2=104, A2=110, AS2=117, B2=123, C3=131,
            CS3=139, D3=147, DS3=156, E3=165, F3=175, FS3=185, G3=196, GS3=208,
            A3=220, AS3=233, B3=247, C4=262, CS4=277, D4=294, DS4=311, E4=330,
            F4=349, FS4=370, G4=392, GS4=415, A4=440,
            AS4=466, B4=494, C5=523, CS5=554, D5=587, DS5=622, E5=659, F5=698,
            FS5=740, G5=784, GS5=831, A5=880, AS5=932, B5=988, C6=1047,
            CS6=1109, D6=1175, DS6=1245, E6=1319, F6=1397, FS6=1480, G6=1568,
            GS6=1661, A6=1760, AS6=1865, B6=1976, C7=2093, CS7=2217, D7=2349,
            DS7=2489, E7=2637, F7=2794, FS7=2960, G7=3136, GS7=3322, A7=3520,
            AS7=3729, B7=3951, C8=4186, CS8=4435, D8=4699, DS8=4978)
        if (isinstance(melody, list)) and (isinstance(durations, list)):
            length = len(melody)
            cmd_args = [length, pin]
            if length == len(durations):
                cmd_args.extend([NOTES.get(melody[note])
                                for note in range(length)])
                cmd_args.extend([durations[duration]
                                for duration in range(len(durations))])
                cmd_str = self.build_cmd_str("to", cmd_args)
                try:
                    self.sr.write(cmd_str.encode())
                    self.sr.flush()
                except:
                    pass
                cmd_str = self.build_cmd_str("nto", [pin])
                try:
                    self.sr.write(cmd_str.encode())
                    self.sr.flush()
                except:
                    pass
            else:
                return -1
        else:
            return -1

    def capacitivePin(self, pin):
        '''
        Input:
            pin (int): pin to use as capacitive sensor

        Use it in a loop!
        DO NOT CONNECT ANY ACTIVE DRIVER TO THE USED PIN !

        the pin is toggled to output mode to discharge the port,
        and if connected to a voltage source,
        will short circuit the pin, potentially damaging
        the Arduino/Shrimp and any hardware attached to the pin.
        '''
        cmd_str = self.build_cmd_str("cap", (pin,))
        self.sr.write(cmd_str.encode())
        rd = self.sr.readline().decode("utf-8").replace("\r\n", "")
        if rd.isdigit():
            return int(rd)

    def shiftOut(self, dataPin, clockPin, pinOrder, value):
        """
        Shift a byte out on the datapin using Arduino's shiftOut()

        Input:
            dataPin (int): pin for data
            clockPin (int): pin for clock
            pinOrder (String): either 'MSBFIRST' or 'LSBFIRST'
            value (int): an integer from 0 and 255
        """
        cmd_str = self.build_cmd_str("so",
                               (dataPin, clockPin, pinOrder, value))
        self.sr.write(cmd_str.encode())
        self.sr.flush()

    def shiftIn(self, dataPin, clockPin, pinOrder):
        """
        Shift a byte in from the datapin using Arduino's shiftIn().

        Input:
            dataPin (int): pin for data
            clockPin (int): pin for clock
            pinOrder (String): either 'MSBFIRST' or 'LSBFIRST'
        Output:
            (int) an integer from 0 to 255
        """
        cmd_str = self.build_cmd_str("si", (dataPin, clockPin, pinOrder))
        self.sr.write(cmd_str.encode())
        self.sr.flush()
        rd = self.sr.readline().decode("utf-8").replace("\r\n", "")
        if rd.isdigit():
            return int(rd)


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
            args = '%'.join(map(str, args))
        else:
            args = ''
        return "@{cmd}%{args}$!".format(cmd=cmd, args=args)
    
    
    def get_version(self,sr):
        cmd_str = self.build_cmd_str("version")
        try:
            sr.write(cmd_str.encode())
            sr.flush()
        except Exception:
            return None
        return sr.readline().replace("\r\n", "")
