classdef tclab
   properties
      device
      board
      platform
      lab
   end
   methods
      function obj = tclab(com)
         % connect to Arduino
         board = 'Leonardo';
         try
             % Install Arduino support with "pkg install -forge arduino"
             % See https://wiki.octave.org/Arduino_package
             pkg load arduino
             platform = 'octave';
         catch
             % Install Arduino support with Arduino support package
             platform = 'matlab';
         end
         
         try
             if nargin==0
                 lab = arduino;
             else
                 disp(['Connecting on COM port: ',com])
                 lab = arduino(com,board);
             end
         catch
             disp('Arduino reset, setup, or COM port needed')
             disp('1. Reset the Arduino (recommended if connected previously)')
             disp('2. Run "arduinosetup" from the command line to load firmware (if not previously connected)')
             disp('3. If still unable to connect, try COM port input with: lab=tclab("COM4")')
             disp('')
             disp('For Windows:')
             disp('  Open device manager, select "Ports (COM & LPT)"')
             disp('  Look for COM port of Arduino such as COM4')
             disp('For MacOS:')
             disp('  Open terminal and type: ls /dev/*.')
             disp('  Search for /dev/tty.usbmodem* or /dev/tty.usbserial*. The port number is *.')
             disp('For Linux')
             disp('  Open terminal and type: ls /dev/tty*')
             disp('  Search for /dev/ttyUSB* or /dev/ttyACM*. The port number is *.')
             disp('')
             stop
         end
         obj.device = 'TCLab';
         obj.board = board;
         obj.platform = platform;
         obj.lab = lab;
      end
      function r = v1a(obj)
         r=readVoltage(obj.lab, 'A0');
      end
      function r = v2a(obj)
         r=readVoltage(obj.lab, 'A2');
      end
      function r = v1(obj,n)
         r = 0;
         for i = 1:n
             r = r + obj.v1a;
         end
         r = r/n;
      end
      function r = v2(obj,n)
         r = 0;
         for i = 1:n
             r = r + obj.v2a;
         end
         r = r/n;
      end
      function r = TC(obj,V)
         r = (V - 0.5)*100.0;
      end
      function r = T1(obj)
         r = obj.TC(obj.v1(10));
      end
      function r = T2(obj)
         r = obj.TC(obj.v2(10));
      end
      function r = LED(obj,level)
         % LED function (0 <= level <= 100)
         if obj.platform=='octave'
             pkg load arduino
         end
         writePWMDutyCycle(obj.lab,'D9',max(0,min(1,level/100)));
         r = level;
      end
      function r = Q1(obj,level)
         % heater output (0 <= heater <= 100)
         % limit to 0-0.9 (0-100%)
         if obj.platform=='octave'
             pkg load arduino
         end
         writePWMDutyCycle(obj.lab,'D3',max(0,min(100,level))*0.9/100);
         r = level;
      end
      function r = Q2(obj,level)
         % heater output (0 <= heater <= 100)
         % limit to 0-0.5 (0-100%)
         if obj.platform=='octave'
             pkg load arduino
         end
         writePWMDutyCycle(obj.lab,'D5',max(0,min(100,level))*0.5/100);
         r = level;
      end
      function r = off(obj)
         if obj.platform=='octave'
             pkg load arduino
         end
         writePWMDutyCycle(obj.lab,'D3',0);
         writePWMDutyCycle(obj.lab,'D5',0);
         writePWMDutyCycle(obj.lab,'D9',0);
         r = 'TCLab heaters and LED off';
      end
      function r = blink(obj,sec)
         obj.LED(100);
         pause(sec);
         obj.LED(0);
         r = ['LED Blink for ',num2str(sec),' sec'];
      end
      function r = test(obj)
         disp('30 Second Test, Turn on Heaters to 100%')
         obj.Q1(100);  obj.Q2(100);
         for i = 1:30
             disp([' T1: ' num2str(obj.T1)...
                   ' T2: ' num2str(obj.T2)])
             % blink LED each cycle
             obj.LED(100); pause(0.8); obj.LED(0); pause(0.2)
         end
         disp('Turn off heaters')
         obj.off();
         r = ['TCLab test complete'];
      end
   end
end
