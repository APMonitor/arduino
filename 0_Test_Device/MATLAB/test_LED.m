close all; clear all; clc

try
    a = arduino;
    disp(a)
catch
    warning('Unable to connect, user input required')
    disp('For Windows:')
    disp('  Open device manager, select "Ports (COM & LPT)"')
    disp('  Look for COM port of Arduino such as COM4')
    com_port = input('Specify COM port (e.g. COM4): ','s');
    com_port = upper(com_port);
    a = arduino(com_port,'Uno');
    disp(a)
end
    
% Write data to the digital pin
disp('LED on and off repeatedly for 5 seconds')
for i = 0:5
    writeDigitalPin(a,'D9',1);
    pause(0.5);
    writeDigitalPin(a,'D9',0);
    pause(0.5);
end

% Change the brightness from maximum to minimum using the
%  digital pin's PWM duty cycle.
disp('LED dimming from bright to off over 10 seconds')
for brightness = 1:-0.1:0
    writePWMDutyCycle(a,'D9',brightness);
    pause(1.0);
end

disp('LED Test Complete')
