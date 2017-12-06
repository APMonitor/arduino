% connect to Arduino
try
    a = arduino;
    disp(a)
catch
    warning('Unable to connect, user input required')
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
    com_port = input('Specify port (e.g. COM4 for Windows or /dev/ttyUSB0 for Linux): ','s');
    a = arduino(com_port,'Uno');
    disp(a)
end

% voltage read functions
v1 = @() readVoltage(a, 'A0');
v2 = @() readVoltage(a, 'A2');

% temperature calculations as a function of voltage for TMP36
TC = @(V) (V - 0.5)*100.0;          % Celsius
TK = @(V) TC(V) + 273.15;           % Kelvin
TF = @(V) TK(V) * 9.0/5.0 - 459.67; % Fahrenhiet

% temperature read functions
T1C = @() TC(v1());
T2C = @() TC(v2());

% LED function (0 <= level <= 1)
led = @(level) writePWMDutyCycle(a,'D9',max(0,min(1,level)));  % ON

% heater output (0 <= heater <= 100)
% limit to 0-0.9 (0-100%)
h1 = @(level) writePWMDutyCycle(a,'D3',max(0,min(100,level))*0.9/100);
% limit to 0-0.5 (0-100%)
h2 = @(level) writePWMDutyCycle(a,'D5',max(0,min(100,level))*0.5/100);
