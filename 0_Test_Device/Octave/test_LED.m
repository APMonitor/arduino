clear all
lab = tclab; % include tclab.m
lab.LED(100); disp('LED on')
pause(5); % Pause for 5 seconds
lab.LED(0); disp('LED off')
lab.off(); clear lab