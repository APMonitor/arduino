function [outputs] = mpc(inputs)

persistent first s c

if isempty(first)
    % initialization
    s = 'http://byu.apmonitor.com';
    c = 'mpc';
    addpath('apm')
    msg = mpc_init(s,c);
    disp(msg)
end

T_sp = inputs(1);
T_meas = inputs(2);

% input measurement
apm_meas(s,c,'TC',T_meas);

% input setpoint with deadband +/- DT
DT = 0.1;
apm_option(s,c,'TC.sphi',T_sp+DT);
apm_option(s,c,'TC.splo',T_sp-DT);

% solve MPC
output = apm(s,c,'solve');

% test for successful solution
if (apm_tag(s,c,'apm.appstatus')==1)
    % retrieve the first Q value
    Q1 = apm_tag(s,c,'Q1.Newval');
else
    % display output for debugging
    print(output)
    % not successful, set voltage to zero
    Q1 = 0;
end

% send to output
outputs = Q1;

if isempty(first)
    apm_web(s,c);
    first = false;
end

end


