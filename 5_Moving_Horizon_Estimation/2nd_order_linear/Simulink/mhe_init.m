function msg = mhe_init(s,b)
addpath('apm')
apm(s,b,'clear all');

% load model and data
apm_load(s,b,'model.apm');
csv_load(s,b,'mhe.csv');

% configure MV / CV
apm_info(s,b,'FV','Kp');
apm_info(s,b,'FV','tau');
apm_info(s,b,'FV','zeta');
apm_info(s,b,'FV','TC_ss');
apm_info(s,b,'MV','Q1');
apm_info(s,b,'CV','TC');

% dynamic estimation
apm_option(s,b,'nlc.imode',5);
apm_option(s,b,'nlc.solver',3);

% tune FV
apm_option(s,b,'Kp.dmax',0.05);
apm_option(s,b,'Kp.lower',0.3);
apm_option(s,b,'Kp.upper',0.6);
apm_option(s,b,'tau.dmax',2.0);
apm_option(s,b,'tau.lower',40.0);
apm_option(s,b,'tau.upper',60.0);
apm_option(s,b,'zeta.dmax',0.05);
apm_option(s,b,'zeta.lower',1.3);
apm_option(s,b,'zeta.upper',1.7);
apm_option(s,b,'TC_ss.dmax',1.0);
apm_option(s,b,'TC_ss.lower',22.0);
apm_option(s,b,'TC_ss.upper',25.0);
% turn on FVs as degrees of freedom
apm_option(s,b,'Kp.status',1);
apm_option(s,b,'tau.status',1);
apm_option(s,b,'zeta.status',1);
apm_option(s,b,'TC_ss.status',1);

apm_option(s,b,'Kp.fstatus',0);
apm_option(s,b,'tau.fstatus',0);
apm_option(s,b,'zeta.fstatus',0);
apm_option(s,b,'TC_ss.fstatus',0);

% read Q, don't let optimize use MV
apm_option(s,b,'Q1.status',0);
apm_option(s,b,'Q1.fstatus',1);
% include CV in objective function
apm_option(s,b,'TC.status',1);
apm_option(s,b,'TC.fstatus',1);

% web-viewer option, update every second
apm_option(s,b,'nlc.web_plot_freq',2);

msg = 'initialization complete';

end