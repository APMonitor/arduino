close all; clear all; clc

% include tclab.m for initialization
tclab;

% Test device
disp(['Temperature 1: ' num2str(T1C()) ' degC'])
disp(['Temperature 2: ' num2str(T2C()) ' degC'])

disp('Turn on Heater 1 to 30%, Heater 2 to 60%')
h1(30);  h2(60);

disp('Turn on LED for 30 seconds')
led(1);   % ON
pause(30.0);
led(0); % OFF

disp('Turn off Heaters')
h1(0);  h2(0);

disp(['Temperature 1: ' num2str(T1C()) ' degC'])
disp(['Temperature 2: ' num2str(T2C()) ' degC'])

disp('Temperature Test Complete')
