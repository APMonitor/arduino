function [outputs] = mhe_apm(inputs)

persistent first s b

if isempty(first)
    % initialization
    addpath('apm')
    s = 'http://byu.apmonitor.com';
    b = ['mhe' int2str(rand()*10000)];
    msg = mhe_init(s,b);
    disp(msg)
end

T1_meas = inputs(1);
T2_meas = inputs(2);
Q1 = inputs(3);
Q2 = inputs(4);

% input measurements
apm_meas(s,b,'TC1',T1_meas);
apm_meas(s,b,'TC2',T2_meas);
apm_meas(s,b,'Q1',Q1);
apm_meas(s,b,'Q2',Q2);

% solve MPC
output = apm(s,b,'solve');

% test for successful solution
if (apm_tag(s,b,'apm.appstatus')==1)
    % retrieve the parameter values
    
    % option %2 retrieval (apm_tag)
    U = apm_tag(s,b,'U.Newval');
    tau = apm_tag(s,b,'tau.Newval');
    a1 = apm_tag(s,b,'a1.Newval');
    a2 = apm_tag(s,b,'a2.Newval');
    Ta = apm_tag(s,b,'Ta.Newval');
    TC1 = apm_tag(s,b,'TC1.Model');
    TC2 = apm_tag(s,b,'TC2.Model');
else
    % display output for debugging
    disp(output)
    % not successful, set default parameters
    U = 2.5;
    tau = 5;
    a1 = 0.005;
    a2 = 0.0025;
    Ta = 23;
    TC1 = 23.0;
    TC2 = 23.0;
end
params(1) = U;
params(2) = tau;
params(3) = a1;
params(4) = a2;
params(5) = Ta;

outputs = params;

if isempty(first)
    apm_web(s,b);
    first = false;
end

return