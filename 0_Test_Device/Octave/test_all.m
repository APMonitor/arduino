close all; clear all; clc
lab = tclab;

disp('Turn on Heater 1 to 100%, Heater 2 to 60%')
lab.Q1(100);  lab.Q2(60);

for i = 1:30
    disp([' T1: ' num2str(lab.T1)...
          ' T2: ' num2str(lab.T2)])
    % blink LED each cycle
    lab.LED(100); pause(0.7); lab.LED(0); pause(0.3)
end

% turn off and disconnect
lab.off(); clear lab
