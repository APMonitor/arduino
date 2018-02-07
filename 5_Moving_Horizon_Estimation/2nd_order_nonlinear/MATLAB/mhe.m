function params = mhe(T1_meas,T2_meas,Q1,Q2)

s = 'http://byu.apmonitor.com';
b = 'mhe';
% input measurements
apm_meas(s,b,'TC1',T1_meas);
apm_meas(s,b,'TC2',T2_meas);
apm_meas(s,b,'Q1',Q1);
apm_meas(s,b,'Q2',Q2);

% solve MPC
output = apm(s,b,'solve');
%disp(output)

% test for successful solution
if (apm_tag(s,b,'nlc.appstatus')==1)
    % retrieve the parameter values
    
    % option %2 retrieval (apm_tag)
    U = apm_tag(s,b,'U.Newval');
    tau = apm_tag(s,b,'tau.Newval');
    a1 = apm_tag(s,b,'a1.Newval');
    a2 = apm_tag(s,b,'a2.Newval');
    TC1 = apm_tag(s,b,'TC1.Model');
    TC2 = apm_tag(s,b,'TC2.Model');
else
    % display output for debugging
    disp(output)
    % not successful, set default parameters
    U = 10.0;
    tau = 5;
    a1 = 0.01;
    a2 = 0.0075;
    TC1 = 23.0;
    TC2 = 23.0;
end
params(1) = U;
params(2) = tau;
params(3) = a1;
params(4) = a2;
params(5) = TC1;
params(6) = TC2;

end


