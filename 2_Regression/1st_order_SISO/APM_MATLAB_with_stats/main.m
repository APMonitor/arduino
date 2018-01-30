% Clear local variables and plots
clc; clear all; close all

% Add APM libraries to path for session
addpath('apm');

% specify s=server and a=application names
s = 'http://byu.apmonitor.com';
a = ['temperature' int2str(rand()*1000)];

% clear previous applicaiton by that name
apm(s,a,'clear all');

% load model and data files
apm_load(s,a,'data.apm');
csv_load(s,a,'data.csv');

% change to dynamic simulation
apm_option(s,a,'nlc.imode',5);
apm_option(s,a,'nlc.ev_type',1);
apm_option(s,a,'nlc.solver',1);

% specify parameters to estimate
apm_info(s,a,'FV','K');
apm_info(s,a,'FV','tau');
apm_option(s,a,'K.status',1);
apm_option(s,a,'tau.status',1);
apm_option(s,a,'K.lower',0.1);
apm_option(s,a,'tau.lower',60);
apm_option(s,a,'K.upper',0.5);
apm_option(s,a,'tau.upper',300);

% specify time varying input(s)
apm_option(s,a,'MV','voltage');

% specify variable(s) to fit to data
apm_info(s,a,'CV','temperature');
apm_option(s,a,'temperature.fstatus',1);
apm_option(s,a,'temperature.meas_gap',4);

% Solve model and return solution
output = apm(s,a,'solve')
disp(output);

% Retrieve the results
y = apm_sol(s,a);
z = y.x;
sse = apm_tag(s,a,'nlc.objfcnval');

% display results
k = z.k(1);
tau = z.tau(1);
disp(['New Value of K (Gain): ' num2str(k)]);
disp(['New Value of Tau (Time Constant): ' num2str(tau)]);
disp(['L1 Norm Objective Function: ' num2str(sse)]);

% open web-viewer
apm_web(s,a);

% Retrieve measured values
load data.txt
time_meas = data(:,1);
volt_meas = data(:,2);
temp_meas = data(:,3);

% Plot results
figure(1)
subplot(2,1,1)
plot(z.time,z.voltage,'g-')
legend('Voltage')
ylabel('Voltage (mV)')
subplot(2,1,2)
plot(z.time,z.temperature,'k--')
hold on
plot(time_meas,temp_meas,'r-')
hold on
ylabel('Temperature (degF)')
legend('Predicted Temperature','Measured Temperature')


%%
% Generate contour plot of SSE ratio vs. Parameters
% design variables at mesh points between 0.5 - 2.0 of the optimal values
k = 0.255487983;
tau = 231.4510971;
% meshgrid is +/- 1% change in the objective 
[k,tau] = meshgrid(k*0.99:k*0.0005:k*1.01,tau*0.98:tau*0.001:tau*1.02);

dt = 1; % delta time step
v0 = volt_meas(1); % initial voltage
t0 = temp_meas(1); % initial temperature
n = size(temp_meas,1); % number of measurements
p = 2; % number of parameters

c = exp(-dt./tau);
[s1,s2] = size(c);
v = volt_meas;
t(1,:,:) = t0 * ones(size(c));
sse = zeros(size(c));
for i = 2:n,
    t(i,:,:) = (reshape(t(i-1,:,:),s1,s2)-t0) .* c + v(i-1) .* k .* (1.0 - c) + t0;
    sse = sse + (reshape(t(i,:,:),s1,s2)-temp_meas(i)).^2;
end
% normalize to the best solution
best_sse = min(min(sse))
fsse = (sse - best_sse)/ best_sse ;

% compute f-statistic for the f-test
alpha = 0.05;
flim = p / (n-p) * finv(1-alpha,p,n-p);
disp(['f-test limit for SSE fractional deviation: ' num2str(flim)]);
obj_lim = flim * best_sse + best_sse;

figure(2)
%lines = linspace(0,0.01,0.1);
[C,h] = contour(k,tau,sse);
clabel(C,h,'Labelspacing',250);
title('Contour Plot');
xlabel('Gain (K)');
ylabel('Time Constant (\tau)');
hold on;
% solid line to show confidence region
% flim too small to plot - it is just a point
[C,h] = contour(k,tau,sse,[obj_lim,obj_lim],'r-','LineWidth',2);
clabel(C,h,'Labelspacing',250);
legend('Objective','Confidence Region')
