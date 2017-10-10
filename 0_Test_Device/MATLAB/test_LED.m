close all; clear all; clc

% include tclab.m for initialization
tclab;

% Write data to the digital pin
disp('LED on and off repeatedly for 5 seconds')
for i = 0:5
    led(1)
    pause(0.5);
    led(0)
    pause(0.5);
end

% Change the brightness from maximum to minimum using the
%  digital pin's PWM duty cycle.
disp('LED dimming from bright to off over 10 seconds')
for brightness = 1:-0.1:0
    led(brightness);
    pause(1.0);
end

disp('LED Test Complete')
