function msg = mpc_init(s,c)
    apm(s,c,'clear all');

    % load model and data
    apm_load(s,c,'model.apm');
    csv_load(s,c,'mpc_data.csv');

    % configure MV / CV
    apm_info(s,c,'MV','Q1');
    apm_info(s,c,'MV','Q2');
    apm_info(s,c,'CV','TC1');
    apm_info(s,c,'CV','TC2');

    % dynamic control
    apm_option(s,c,'apm.imode',6);
    apm_option(s,c,'apm.solver',3);
    apm_option(s,c,'apm.hist_hor',600);
    apm_option(s,c,'apm.mv_type',0);
    apm_option(s,c,'apm.cv_type',1);

    % tune MV
    % delta MV movement penalty
    apm_option(s,c,'Q1.dcost',1.0e-4);
    apm_option(s,c,'Q2.dcost',1.0e-4);
    % penalize energy use
    apm_option(s,c,'Q1.cost',0.0);
    apm_option(s,c,'Q2.cost',0.0);
    % limit MV movement each cycle
    apm_option(s,c,'Q1.dmax',50);
    apm_option(s,c,'Q2.dmax',50);
    % MV limits
    apm_option(s,c,'Q1.upper',100);
    apm_option(s,c,'Q1.lower',0);
    apm_option(s,c,'Q2.upper',100);
    apm_option(s,c,'Q2.lower',0);

    % tune CV
    % how fast to reach setpoint
    apm_option(s,c,'TC1.tau',10);
    apm_option(s,c,'TC2.tau',10);
    % trajectory type
    apm_option(s,c,'TC1.tr_init',2);
    apm_option(s,c,'TC2.tr_init',2);

    % let optimizer use MV
    apm_option(s,c,'Q1.status',1);
    apm_option(s,c,'Q2.status',1);
    % include CV in objective function
    apm_option(s,c,'TC1.status',1);
    apm_option(s,c,'TC2.status',1);

    % feedback status (whether we have measurements)
    apm_option(s,c,'Q1.fstatus',0);
    apm_option(s,c,'Q2.fstatus',0);
    apm_option(s,c,'TC1.fstatus',1);
    apm_option(s,c,'TC2.fstatus',1);

    % web-viewer option, update every second
    apm_option(s,c,'apm.web_plot_freq',3);

    msg = 'initialization complete';
end