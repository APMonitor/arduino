#!/usr/bin/env python
import serial
import time
from serial.tools import list_ports
from serial import SerialException
import pandas as pd
import pyqtgraph as pg
import numpy as np
import statsmodels.api as sm
import os
import sys

class Arduino(object):

    def __init__(self, baud=9600, port=None, timeout=2, sr=None):
        # Check to make sure output data file is closed        
        try:
            myfile = open("OutputFiles/data.xls",'w')
            myfile.close()
        except:
            print('**********************************************************')
            print('***Please close data.xls file before starting new run.****')
            print('**********************************************************')
            sys.exit()
        # Connect to serial port
        port = self.findPort()
        print('Opening connection')
        self.s = serial.Serial(port=port, baudrate=115200, timeout=2)
        time.sleep(3)
#        self.s.port = port
#        try:
#            self.s.open()
#        except SerialException:
#            self.s.close()
#            self.s.open()
        self.sr = self.s
        self.tempInPin = 0
        self.voltOutPin = 3
        print('Arduino connected on port '+port)
        print('Current configuration is:')
        print('Read temperature on analog pin '+ str(self.tempInPin))
        print('Write voltage on digital pin '+ str(self.voltOutPin))
        
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
        self.data = np.array([[0, 0, self.readTemp(), 0]])        
        
        # Create figure window
        self.win = pg.GraphicsWindow()
        self.win.resize(1000,600)
        self.win.setWindowTitle('Arduino Temperature Control Lab')
        pg.setConfigOptions(antialias=True)
        
        # Create temperature plot
        self.plt = self.win.addPlot(title="Temperature vs Time",row=1,col=1)
        self.plt.setRange(yRange=[280,380])
        yaxis = self.plt.getAxis('left')
        labelStyle = {'color': '#FFF', 'font-size': '14pt'}
        yaxis.setLabel('Temperature','K', **labelStyle)
        yaxis.setGrid(150)
        
        # Create voltage plot
        self.plt2 = self.win.addPlot(row=2,col=1)
        self.plt2.setRange(yRange=[0,255])
        xaxis = self.plt2.getAxis('bottom')
        xaxis.setLabel('Time','s', **labelStyle)
        yaxis2 = self.plt2.getAxis('left')
        yaxis2.setLabel('Voltage','mV', **labelStyle)
        yaxis2.setGrid(100)
        return True
        
    def addData(self,newData):
        self.data = np.r_[self.data,newData]
        return True
    
    def updatePlots(self):
        self.plt.plot(self.data[-300:,0],self.data[-300:,2], pen=pg.mkPen('r',width=3),clear=True)
        self.plt2.plot(self.data[-300:,0],self.data[-300:,1], pen=pg.mkPen('b',width=3),clear=True)
        self.plt.addLine(y=self.data[-1,3])
        pg.QtGui.QApplication.processEvents()
        return True
        
    def saveData(self):
        df = pd.DataFrame(self.data)
        C = ['Time (s)', 'Voltage Out (mV)', 'Temperature (K)', 'T Setpoint (K)']
        df.to_excel("OutputFiles/data.xls", header=C, index=False)
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
        
    def writeVoltage(self,mV):
        self.analogWrite(self.voltOutPin,mV)
        return True
        
    def stepTest(self,values):
        print('Beginning Step Test. Press Ctrl-C to end data collection')
        start_time = time.time()
        for v in values:
            print('Input: ' + str(v))
            i = 0
            # Main Loop
            try:
                print('Running Step Test.')
                while True:
                        i = i+1
                        # Check for convergence to steady state
                        if(len(self.data)>1000 and i>1000):
                            dx = self.data[-999:,2] - self.data[-1000:-1,2]
                            dt = self.data[-999:,0] - self.data[-1000:-1,0]
                            dxdt = dx/dt
                            if(np.mean(np.abs(dxdt))<=.25):
                                i = 0
                                break
                            
                        # Read write and record
                        time_elapsed = time.time() - start_time
                        tempK = self.readTemp()
                        outputVoltage = v
                        self.writeVoltage(outputVoltage)
                        newData = np.array([[time_elapsed,outputVoltage,tempK,0]])
                        self.addData(newData)
                        self.updatePlots()
                        time.sleep(1.0)
    
            # Allow user to end loop with Ctrl-C           
            except KeyboardInterrupt:
                print('Interrupting Step Test')
                # Write data to file
                self.saveData()
                # Disconnect from Arduino
                self.writeVoltage(0)
                print('Shutting down')
                self.close()
                return True
                return False
        print('Step Test Completed')
        # Write data to file
        self.saveData()
        # Disconnect from Arduino
        self.writeVoltage(0)
        print('Shutting down')
        self.close()
        return True
        
    def doubletTest(self,values):
        print('Beginning Doublet Test. Press Ctrl-C to end data collection')
        start_time = time.time()
        for v in values:
            print('Input: ' + str(v))
            i = 0
            # Main Loop
            try:
                print('Running Doublet Test.')
                while True:
                        i = i+1
                        # Check for convergence to steady state
                        if(len(self.data)>1000 and i>1000):
                            dx = self.data[-999:,2] - self.data[-1000:-1,2]
                            dt = self.data[-999:,0] - self.data[-1000:-1,0]
                            dxdt = dx/dt
                            if(np.mean(np.abs(dxdt))<=.25):
                                print('Step Completed, Moving to next Step')
                                i = 0
                                break
                            
                        # Read write and record
                        time_elapsed = time.time() - start_time
                        tempK = self.readTemp()
                        outputVoltage = v
                        self.writeVoltage(outputVoltage)
                        newData = np.array([[time_elapsed,outputVoltage,tempK,0]])
                        self.addData(newData)
                        self.updatePlots()
                        time.sleep(1.0)
    
            # Allow user to end loop with Ctrl-C           
            except KeyboardInterrupt:
                print('Interrupting Doublet Test')
                # Write data to file
                self.saveData()
                # Disconnect from Arduino
                self.writeVoltage(0)
                print('Shutting down')
                self.close()
                return True
                return False
        print('Doublet Test Completed')
        # Write data to file
        self.saveData()
        # Disconnect from Arduino
        self.writeVoltage(0)
        print('Shutting down')
        self.close()
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
