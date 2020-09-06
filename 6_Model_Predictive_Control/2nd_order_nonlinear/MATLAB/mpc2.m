function [Q1,Q2] = mpc2(T1_meas,T1_sp,T2_meas,T2_sp)

s = 'http://byu.apmonitor.com';
c = 'mpc';

% input measurement
apm_meas(s,c,'TC1',T1_meas);
apm_meas(s,c,'TC2',T2_meas);

% input setpoint with deadband +/- DT
DT = 0.1;
apm_option(s,c,'TC1.sphi',T1_sp+DT);
apm_option(s,c,'TC1.splo',T1_sp-DT);
apm_option(s,c,'TC2.sphi',T2_sp+DT);
apm_option(s,c,'TC2.splo',T2_sp-DT);

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

end


