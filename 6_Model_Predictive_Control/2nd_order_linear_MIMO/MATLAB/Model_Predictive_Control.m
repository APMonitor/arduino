clear all; close all; clc

addpath('apm')

s = 'http://byu.apmonitor.com';
c = 'mpc';

% Connect to Arduino
tclab;

% Run time in minutes
run_time = 10.0;

% Number of cycles (1 cycle per 3 seconds)
loops = round(20*run_time);

% Temperature (degC)
T1 = ones(1,loops) * T1C(); % measured T
Tsp1 = ones(1,loops) * 30;  
T2 = ones(1,loops) * T2C(); % measured T
Tsp2 = ones(1,loops) * 23;  
time = zeros(1,loops);

% Changes in set point
Tsp1(3:end) = 40.0;
Tsp2(40:end) = 30.0;
Tsp1(80:end) = 32.0;
Tsp2(120:end) = 35.0;
Tsp1(160:end) = 45.0;

% milli-volts input
Q1 = zeros(1,loops);
Q2 = zeros(1,loops);

% model predictive control initialization
mpc_init(s,c);

start_time = clock;
prev_time = start_time;

% dynamic plot (note: subplots needs to be declared here first)
figure(1)
subplot(3,1,1)
hold on, grid on
anexp1 = animatedline('LineStyle','-', 'Color', 'k', 'LineWidth', 2);
ansp1 = animatedline('LineStyle','--','Color', 'r','LineWidth', 2);
ylabel('Temperature \circC')
legend('T_1 Measured', 'T_1 Set Point', ...
    'Location', 'northwest')
subplot(3,1,2)
hold on, grid on
anexp2 = animatedline('LineStyle','-', 'Color', 'k', 'LineWidth', 2);
ansp2 = animatedline('LineStyle','--','Color', 'r','LineWidth', 2);
ylabel('Temperature \circC')
legend('T_2 Measured', 'T_2 Set Point', ...
    'Location', 'northwest')
subplot(3,1,3)
hold on, grid on
anQ1 = animatedline('LineStyle','-', 'Color', 'k', 'LineWidth', 2);
anQ2 = animatedline('LineStyle','--', 'Color', 'b', 'LineWidth', 2);
ylabel('Power Level Q (%)')
legend('Q_1', 'Q_2', 'Location', 'northwest')
xlabel('Time (sec)')

for ii = 2:loops    
    % Pause Sleep time
    pause_max = 3.0;
    pause_time = pause_max - etime(clock,prev_time);
    if pause_time >= 0.0
        pause(pause_time - 0.01)
    else
        pause(0.01)
    end
    
    % Record time and change in time
    t = clock;
    dt = etime(t,prev_time);
    if ii>=2
        time(ii) = time(ii-1) + dt;
    end
    prev_time = t;

    % read and record from temperature controller
    T1(ii) = T1C();
    T2(ii) = T2C();
    
    % model predictive control
    [Q1(ii), Q2(ii)] = mpc2(T1(ii),Tsp1(ii),T2(ii),Tsp2(ii));
    
    % adjust power level
    h1(Q1(ii));
    h2(Q2(ii));
    
    % plot
    addpoints(anexp1,time(ii),T1(ii))
    addpoints(ansp1,time(ii),Tsp1(ii))
    addpoints(anexp2,time(ii),T2(ii))
    addpoints(ansp2,time(ii),Tsp2(ii))
    addpoints(anQ1,time(ii),Q1(ii))
    addpoints(anQ2,time(ii),Q2(ii))
    drawnow
    
    if ii==10
        apm_web(s,c);
    end
end

h1(0);
h2(0);
disp('Heaters off')
% turn off heater but keep LED on if T > 50
if (T1C() || T2C()) > 50
    led(1)
    disp(['Warning, heater temperature 1 =', num2str(T1C())])
    disp(['Warning, heater temperature 2 =', num2str(T2C())])
else
    led(0)
end

% save txt file with data
data = [time',Q1',Q2',T1',T2',Tsp1',Tsp2'];
csvwrite('data.txt',data);