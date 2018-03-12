function [outputs] = mpc_apm(inputs)

persistent first s c

if isempty(first)
    % initialization
    addpath('apm')
    s = 'http://byu.apmonitor.com';
    c = ['mpc' int2str(rand()*10000)];
    msg = mpc_init(s,c);
    disp(msg)
end

% inputs to block
T1_sp = inputs(1);
T2_sp = inputs(2);
T1_meas = inputs(3);
T2_meas = inputs(4);
U_mhe = inputs(5);
tau_mhe = inputs(6);
alpha1_mhe = inputs(7);
alpha2_mhe = inputs(8);
Ta_mhe = inputs(9);

% input setpoint with deadband +/- DT
DT = 0.2;
apm_option(s,c,'TC1.sphi',T1_sp+DT);
apm_option(s,c,'TC1.splo',T1_sp-DT);
apm_option(s,c,'TC2.sphi',T2_sp+DT);
apm_option(s,c,'TC2.splo',T2_sp-DT);

% input measurements
apm_meas(s,c,'TC1',T1_meas);
apm_meas(s,c,'TC2',T2_meas);
apm_meas(s,c,'U',U_mhe);
apm_meas(s,c,'tau',tau_mhe);
apm_meas(s,c,'alpha1',alpha1_mhe);
apm_meas(s,c,'alpha2',alpha2_mhe);
apm_meas(s,c,'Ta',Ta_mhe);

% solve MPC
output = apm(s,c,'solve');

% test for successful solution
if (apm_tag(s,c,'apm.appstatus')==1)
    % retrieve the first Q value
    Q1 = apm_tag(s,c,'Q1.Newval');
    Q2 = apm_tag(s,c,'Q2.Newval');
else
    % display output for debugging
    disp(output)
    % not successful, set voltage to zero
    Q1 = 0;
    Q2 = 0;
end

outputs(1) = Q1;
outputs(2) = Q2;

if isempty(first)
    apm_web(s,c);
    first = false;
end

end


