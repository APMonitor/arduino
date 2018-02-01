clc; clear all; close all; format shortg

% include tclab
tclab

% simulation time
time = 10;           % time in min
loops = time*60;        % simulation time in seconds

% Measurements and Predictions
time = zeros(1,loops);
T1 = ones(1,loops) * T1C();       % measured T (sensor 1)
T2 = ones(1,loops) * T2C();       % measured T (sensor 2)
Tp1 = ones(1,loops) * T1C();      % pred T1 (energy balance model)
Tp2 = ones(1,loops) * T2C();      % pred T2 (energy balance model)

% Error & Power allocation
error1 = zeros(loops,1);         % error vector for T1 model
error2 = zeros(loops,1);         % error vector for T2 model
Q = zeros(loops,2);
% adjust heater levels
Q(10:end,1) = 100.0;
Q(100:end,2) = 50.0;
Q(200:end,1) = 5.0;
Q(300:end,2) = 80.0;
Q(400:end,1) = 70.0;
Q(500:end,2) = 10.0;

start_time = clock;
prev_time = start_time;

% dynamic plot (note: subplots needs to be declared here first)
figure(1)
subplot(2,1,1)
hold on, grid on
anexp1 = animatedline('LineStyle','-', 'Color', 'k', 'LineWidth', 2);
anexp2 = animatedline('LineStyle','-', 'Color', 'g', 'LineWidth', 2);
anpred1 = animatedline('LineStyle','--','Color', 'b','LineWidth', 2);
anpred2 = animatedline('LineStyle','--','Color', 'r', 'LineWidth', 2);
xlabel('Time (sec)')
ylabel('Temperature \circC')
legend('T_1 Measured', 'T_2 Measured', ...
    'T_1 Predicted', 'T_2 Predicted', ...
    'Location', 'northwest')
title('Temperature Simulation')
subplot(2,1,2)
hold on, grid on
yyaxis left
anerror = animatedline('LineStyle','-', 'Color', 'b', 'LineWidth', 2);
xlabel('Time (sec)')
ylabel('Cumulative Error')
yyaxis right
title('Step and Error Simulation')
anQ1 = animatedline('LineStyle','-', 'Color', 'k', 'LineWidth', 2);
anQ2 = animatedline('LineStyle','--', 'Color', 'r', 'LineWidth', 2);
ylabel('Power Level Q (%)')
xlabel('time (sec)')
legend('Energy Balance Error', 'Q_1', 'Q_2', 'Location', 'northwest')

for ii = 1:loops
    % adjust power level
    Q1s(ii) = Q(ii,1);
    Q2s(ii) = Q(ii,2);
    h1(Q1s(ii));
    h2(Q2s(ii));
    
    % Pause Sleep time
    pause_max = 1.0;
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
    
    % non-linear energy balance
    jj = ii+1;
    [tsim, Tnext_fnd] = ode45(@(tsim,x)energy_bal(tsim,x,...
        Q1s(ii),Q2s(ii)), [0 dt],...
        [Tp1(jj-1)+273.15,Tp2(jj-1)+273.15]);
    Tp1(jj) = Tnext_fnd(end,1) - 273.15;
    Tp2(jj) = Tnext_fnd(end,2) - 273.15;
        
    % read and record from temperature controller
    T1(ii) = T1C();
    T2(ii) = T2C();
    
    % calculate error
    error1(jj) = error1(ii) + dt * abs(T1(ii) - Tp1(ii));
    error2(jj) = error2(ii) + dt * abs(T2(ii) - Tp2(ii));
    error(jj) = error1(jj) + error2(jj);
    
    % plot
    addpoints(anexp1,time(ii),T1(ii))
    addpoints(anexp2,time(ii),T2(ii))
    addpoints(anpred1,time(ii),Tp1(ii))
    addpoints(anpred2,time(ii),Tp2(ii))
    addpoints(anerror,time(ii),error(ii))
    addpoints(anQ1,time(ii),Q1s(ii))
    addpoints(anQ2,time(ii),Q2s(ii))
    drawnow
    
end

disp(['Energy Balance Cumulative Error =', num2str(error(end,1))]);
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
data = [time',Q1s',Q2s',T1',T2'];
csvwrite('data.txt',data);
%save 'data.txt' -ascii data