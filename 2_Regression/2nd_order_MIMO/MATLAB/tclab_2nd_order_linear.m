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
apm_info(s,a,'FV','K1');
apm_info(s,a,'FV','K2');
apm_info(s,a,'FV','K3');
apm_info(s,a,'FV','tau12');
apm_info(s,a,'FV','tau3');
apm_info(s,a,'MV','Q1');
apm_info(s,a,'MV','Q2');
apm_info(s,a,'CV','TC1');
apm_info(s,a,'CV','TC2');

% set status on
apm_option(s,a,'K1.status',1);
apm_option(s,a,'K2.status',1);
apm_option(s,a,'K3.status',1);
apm_option(s,a,'tau12.status',1);
apm_option(s,a,'tau3.status',0);

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
K1 = apm_tag(s,a,'K1.newval');
K2 = apm_tag(s,a,'K2.newval');
K3 = apm_tag(s,a,'K3.newval');
tau12 = apm_tag(s,a,'tau12.newval');
tau3 = apm_tag(s,a,'tau3.newval');

% display values
disp(['K1:   ' num2str(K1)])
disp(['K2:   ' num2str(K2)])
disp(['K3:   ' num2str(K3)])
disp(['tau12:   ' num2str(tau12)])
disp(['tau3:   ' num2str(tau3)])

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
