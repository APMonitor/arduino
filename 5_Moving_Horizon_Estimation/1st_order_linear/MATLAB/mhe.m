function params = mhe(T_meas,Q1)

s = 'http://byu.apmonitor.com';
b = 'mhe';
% input measurements
apm_meas(s,b,'TC',T_meas);
apm_meas(s,b,'Q1',Q1);

% solve MPC
output = apm(s,b,'solve');

% test for successful solution
if (apm_tag(s,b,'nlc.appstatus')==1)
    % retrieve the parameter values
    
    % option %2 retrieval (apm_tag)
    Kp = apm_tag(s,b,'Kp.Newval');
    tau = apm_tag(s,b,'tau.Newval');
    TC_ss = apm_tag(s,b,'TC_ss.Newval');
    TC = apm_tag(s,b,'TC.Model');
else
    % display output for debugging
    disp(output)
    % not successful, set default parameters
    Kp = 0.4;
    tau = 160.0;
    TC_ss = 23.0;
    TC = 23.0;
end
params(1) = Kp;
params(2) = tau;
params(3) = TC_ss;
params(4) = TC;

end


