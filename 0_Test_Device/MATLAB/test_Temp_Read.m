close all; clear all; clc

% temperature calculations as a function of voltage for TMP36
TC = @(V) (V - 0.5)*100.0;      % Celsius
TK = @(V) TC(V) + 273.15;           % Kelvin
TF = @(V) TK(V) * 9.0/5.0 - 459.67; % Fahrenhiet

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
    com_port = input('Specify COM port (e.g. COM4 for Windows or /dev/ttyUSB0 for Linux): ','s');
    a = arduino(com_port,'Uno');
    disp(a)
end

disp('Read temperature sensor 1 (T1)')
v1 = readVoltage(a, 'A0');
T1C = TC(v1);  % Celsius
T1F = TF(v1);  % Fahrenheit
disp(['Temperature 1: ' num2str(v1) 'V' ...
    ' = ' num2str(T1F) 'degF' ...
    ' = ' num2str(T1C) 'degC'])

disp('Read temperature sensor 2 (T2)')
v2 = readVoltage(a, 'A2');
T2C = TC(v2);  % Celcius
T2F = TF(v2);  % Fahrenheit
disp(['Temperature 2: ' num2str(v2) 'V' ...
    ' = ' num2str(T2F) 'degF' ...
    ' = ' num2str(T2C) 'degC'])

disp('Turn on LED for 3 seconds')
writeDigitalPin(a,'D9',1);  % ON
pause(3.0);
writeDigitalPin(a,'D9',0);  % OFF

disp('Temperature Test Complete')
