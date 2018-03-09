close all; clear all; clc

addpath('apm')

s = 'http://byu.apmonitor.com';
a = 'parameter_regression';

% clear application and load new model and data files
apm(s,a,'clear all');
apm_load(s,a,'model.apm');
csv_load(s,a,'data.csv');

% estimation mode
apm_option(s,a,'apm.imode',5);
apm_option(s,a,'apm.solver',3);

% classify variables
apm_info(s,a,'FV','U');
apm_info(s,a,'FV','tau');
apm_info(s,a,'FV','a1');
apm_info(s,a,'FV','a2');
apm_info(s,a,'FV','Ta');
apm_info(s,a,'MV','Q1');
apm_info(s,a,'MV','Q2');
apm_info(s,a,'CV','TC1');
apm_info(s,a,'CV','TC2');

% set status on
apm_option(s,a,'U.status',1);
apm_option(s,a,'tau.status',1);
apm_option(s,a,'a1.status',1);
apm_option(s,a,'a2.status',1);
apm_option(s,a,'Ta.status',1);

% set feedback status on
apm_option(s,a,'Q1.fstatus',1);
apm_option(s,a,'Q2.fstatus',1);
apm_option(s,a,'TC1.fstatus',1);
apm_option(s,a,'TC2.fstatus',1);

% optimize parameters
output = apm(s,a,'solve');
disp(output)

% retrieve solution
y = apm_sol(s,a);
z = y.x;

% optimized parameter values
U = apm_tag(s,a,'U.newval');
tau = apm_tag(s,a,'tau.newval');
a1 = apm_tag(s,a,'a1.newval');
a2 = apm_tag(s,a,'a2.newval');
Ta = apm_tag(s,a,'Ta.newval');

% display values
disp(['U:   ' num2str(U)])
disp(['tau:   ' num2str(tau)])
disp(['a1:   ' num2str(a1)])
disp(['a2:   ' num2str(a2)])
disp(['Ta:   ' num2str(Ta)])

% read data.csv file for plotting
data = csvread('data.csv',1);
t = data(:,1);
T1meas = data(:,4);
T2meas = data(:,5);

% Plot results
figure(1)
subplot(3,1,1)
plot(t/60,T1meas,'b-','LineWidth',2)
hold on
plot(z.time/60,z.tc1,'g:','LineWidth',2)
ylabel('Temperature (degC)')
legend('T_1 measured','T_1 optimized')

subplot(3,1,2)
plot(t/60,T2meas,'k-','LineWidth',2)
hold on
plot(z.time/60,z.tc2,'r:','LineWidth',2)
ylabel('Temperature (degC)')
legend('T_2 measured','T_2 optimized')

subplot(3,1,3)
plot(z.time/60,z.q1,'g-','LineWidth',2)
hold on
plot(z.time/60,z.q2,'k--','LineWidth',2)
ylabel('Heater Output')
legend('Q_1','Q_2')

xlabel('Time (min)')
