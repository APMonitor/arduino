function Q1 = mpc(T_meas,T_sp)

s = 'http://byu.apmonitor.com';
c = 'mpc';

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

end


