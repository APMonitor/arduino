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

disp('Test Heater 1')
disp('LED Indicates Temperature')

figure(1)
T1p = [];
T2p = [];
H1p = [];
H2p = [];
% initial heater values
H1 = 0;
H2 = 0;
writePWMVoltage(a,'D3',H1);
writePWMVoltage(a,'D5',H2);  

for i = 1:290
    tic;
    if i==5
        disp('Turn on heater 1 with 2V (0-5.5V)')
        H1 = 2;
        writePWMVoltage(a,'D3',H1);
    end
    if i==105
        disp('Turn off heater 1')
        H1 = 0;
        writePWMVoltage(a,'D3',H1);
    end
    if i==110
        disp('Turn on heater 2 with 2.5V (0-5.5V)')
        H2 = 2.5;
        writePWMVoltage(a,'D5',H2);
    end
    if i==205
        disp('Turn off heaters')
        H1 = 0;
        H2 = 0;
        writePWMVoltage(a,'D3',H1);
        writePWMVoltage(a,'D5',H2);
    end
    % read temperature 1
    v1 = readVoltage(a, 'A0');
    T1C = TC(v1);
    T1K = TK(v1);
    % read temperature 2
    v2 = readVoltage(a, 'A2');
    T2C = TC(v2);
    T2K = TK(v2);

    % LED brightness
    brightness1 = (T1K - 300.0)/50.0;  % <300K off, >350K full brightness
    brightness2 = (T2K - 300.0)/50.0;  % <300K off, >350K full brightness
    brightness = max(brightness1,brightness2);
    brightness = max(0,min(1,brightness)); % limit 0-1
    writePWMDutyCycle(a,'D9',brightness);
    
    % plot heater and temperature data
    H1p = [H1p,H1];
    H2p = [H2p,H2];
    T1p = [T1p,T1C];
    T2p = [T2p,T2C];
    n = length(T1p);
    time = linspace(0,n+1,n);
    clf
    subplot(2,1,1)
    plot(time,T1p,'r.','MarkerSize',10);
    hold on
    plot(time,T2p,'b.','MarkerSize',10);
    ylabel('Temperature (degC)')
    legend('Temperature 1','Temperature 2','Location','NorthWest')
    subplot(2,1,2)
    plot(time,H1p,'r-','LineWidth',2);
    hold on
    plot(time,H2p,'b--','LineWidth',2);
    ylabel('Heater (0-5.5 V)')
    xlabel('Time (sec)')
    legend('Heater 1','Heater 2','Location','NorthWest')
    drawnow;
    t = toc;
    pause(max(0.01,1.0-t))
end

disp('Turn off heaters')
writePWMVoltage(a,'D3',0);
writePWMVoltage(a,'D5',0);

disp('Heater Test Complete')
