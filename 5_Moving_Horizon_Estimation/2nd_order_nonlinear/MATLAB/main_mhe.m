clear all; close all; clc

addpath('apm')

s = 'http://byu.apmonitor.com';
b = 'mhe';

% Connect to Arduino
tclab;

% Run time in minutes
run_time = 10.0;

% Number of cycles (1 cycle per 3 seconds)
loops = round(20*run_time);

% milli-volts input
Q1 = zeros(1,loops);
Q2 = zeros(1,loops);
Q1(3:end) = 100.0;
Q1(50:end) = 0.0;
Q1(100:end) = 80.0;

Q2(25:end) = 60.0;
Q2(75:end) = 100.0;
Q2(125:end) = 25.0;

for i = 130:180
    if mod(i,10)==0
        Q1(i:i+10) = rand(1) * 100;
    end
    if mod(i+5,10)==0
        Q2(i:i+10) = rand(1) * 100;
    end        
end

% Temperature (degC)
T1 = ones(1,loops) * T1C(); % measured T
T2 = ones(1,loops) * T2C(); % measured T
T1mhe = ones(1,loops) * T1C(); % measured T
T2mhe = ones(1,loops) * T2C(); % measured T
Umhe = ones(1,loops) * 10.0;
taumhe = ones(1,loops) * 5.0;
amhe1 = ones(1,loops) * 0.01;
amhe2 = ones(1,loops) * 0.0075;
time = zeros(1,loops);

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
anexp2 = animatedline('LineStyle','-', 'Color', 'b', 'LineWidth', 2);
anpred2 = animatedline('LineStyle','--','Color', 'g','LineWidth', 2);
ylabel('Temperature \circC')
legend('T_1 Measured', 'T_1 Predicted', ...
    'T_2 Measured', 'T_2 Predicted', ...
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
anU = animatedline('LineStyle','-', 'Color', 'r', 'LineWidth', 2);
antau = animatedline('LineStyle','--', 'Color', 'b', 'LineWidth', 2);
ana1 = animatedline('LineStyle','-', 'Color', 'g', 'LineWidth', 2);
ana2 = animatedline('LineStyle','-', 'Color', 'k', 'LineWidth', 2);
ylabel('Parameters')
legend('U', 'tau', 'a1 x 1000', 'a2 x 1000', 'Location', 'northwest')
xlabel('Time (sec)')

for ii = 1:loops
    % adjust power level
    h1(Q1(ii));
    h2(Q2(ii));
    
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
    
    % Start estimating parameters after 10 cycles (30 sec)
    if ii==10
       apm_option(s,b,'U.STATUS',1);
       apm_option(s,b,'tau.STATUS',1);
       apm_option(s,b,'a1.STATUS',1);
       apm_option(s,b,'a2.STATUS',1);
    end
    
    % non-linear energy balance
    jj = ii+1;
    params = mhe(T1(ii),T2(ii),Q1(ii),Q2(ii));
    Umhe(jj) = params(1);
    taumhe(jj) = params(2);
    a1(jj) = params(3);
    a2(jj) = params(4);
    T1mhe(jj) = params(5);        
    T2mhe(jj) = params(6);        
        
    % plot
    addpoints(anexp1,time(ii),T1(ii))
    addpoints(anpred1,time(ii),T1mhe(ii))
    addpoints(anexp2,time(ii),T2(ii))
    addpoints(anpred2,time(ii),T2mhe(ii))
    addpoints(anQ1,time(ii),Q1(ii))
    addpoints(anQ2,time(ii),Q2(ii))
    addpoints(anU,time(ii),Umhe(ii))
    addpoints(antau,time(ii),taumhe(ii))
    addpoints(ana1,time(ii),1000*a1(ii))
    addpoints(ana2,time(ii),1000*a2(ii))
    drawnow    
    
    % open web-interface
    if ii==20
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