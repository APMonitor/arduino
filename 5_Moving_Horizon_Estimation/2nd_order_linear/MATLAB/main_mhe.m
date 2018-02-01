clear all; close all; clc

addpath('apm')

s = 'http://byu.apmonitor.com';
b = 'mhe';

% Connect to Arduino
tclab;

% Run time in minutes
run_time = 5.0;

% Number of cycles (1 cycle per 2 seconds)
loops = round(30*run_time);

% Temperature (degC)
T1 = ones(1,loops) * T1C(); % measured T
T1mhe = ones(1,loops) * T1C(); % measured T
Kp = ones(1,loops) * 0.3598;
tau = ones(1,loops) * 47.73;
zeta = ones(1,loops) * 1.5;
TC_ss = ones(1,loops) * 23;
time = zeros(1,loops);

% milli-volts input
Q1 = zeros(1,loops);
Q2 = zeros(1,loops);
Q1(6:end) = 100.0;
Q1(50:end) = 20.0;
Q1(100:end) = 80.0;
Q1(150:end) = 10.0;
Q1(200:end) = 95.0;
Q1(250:end) = 0.0;

% time
tm = zeros(1,loops);

% moving horizon estimation
mhe_init();

start_time = clock;
prev_time = start_time;

% dynamic plot (note: subplots needs to be declared here first)
figure(1)
subplot(3,1,1)
hold on, grid on
anexp1 = animatedline('LineStyle','-', 'Color', 'k', 'LineWidth', 2);
anpred1 = animatedline('LineStyle','--','Color', 'r','LineWidth', 2);
ylabel('Temperature \circC')
legend('T_1 Measured', 'T_1 Predicted', ...
    'Location', 'northwest')
title('Temperature Estimation')
subplot(3,1,2)
hold on, grid on
anQ1 = animatedline('LineStyle','-', 'Color', 'k', 'LineWidth', 2);
anQ2 = animatedline('LineStyle','--', 'Color', 'b', 'LineWidth', 2);
ylabel('Power Level Q (%)')
legend('Q_1', 'Q_2', 'Location', 'northwest')
subplot(3,1,3)
hold on, grid on
anK = animatedline('LineStyle','-', 'Color', 'r', 'LineWidth', 2);
antau = animatedline('LineStyle','--', 'Color', 'b', 'LineWidth', 2);
anzeta = animatedline('LineStyle','-', 'Color', 'g', 'LineWidth', 2);
ylabel('Parameters')
legend('K x 100', 'tau', 'zeta x 100', 'Location', 'northwest')
xlabel('Time (sec)')

for ii = 1:loops
    % adjust power level
    h1(Q1(ii));
    h2(Q2(ii));
    
    % Pause Sleep time
    pause_max = 2.0;
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
    
    % non-linear energy balance
    jj = ii+1;
    params = mhe(T1(ii),Q1(ii));
    Kp(jj) = params(1);
    tau(jj) = params(2);
    zeta(jj) = params(3);
    T1mhe(jj) = params(5);        
        
    % plot
    addpoints(anexp1,time(ii),T1(ii))
    addpoints(anpred1,time(ii),T1mhe(ii))
    addpoints(anQ1,time(ii),Q1(ii))
    addpoints(anQ2,time(ii),Q2(ii))
    addpoints(anK,time(ii),100*Kp(ii))
    addpoints(antau,time(ii),tau(ii))
    addpoints(anzeta,time(ii),100*zeta(ii))
    drawnow    
    
    % open web-interface
    if ii==10
        apm_web(s,b);
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
data = [time',Q1',Q2',T1',T2'];
csvwrite('data.txt',data);