function msg = mpc_init(s,c)
    apm(s,c,'clear all');

    % load model and data
    apm_load(s,c,'control.apm');
    csv_load(s,c,'control.csv');

    % configure MV / CV
    apm_info(s,c,'MV','Q1');
    apm_info(s,c,'CV','TC');

    % dynamic control
    apm_option(s,c,'apm.imode',6);
    apm_option(s,c,'apm.solver',3);
    apm_option(s,c,'apm.hist_hor',600);

    % tune MV
    % delta MV movement penalty
    apm_option(s,c,'Q1.dcost',1.0e-4);
    % penalize energy use
    apm_option(s,c,'Q1.cost',0.0);
    % limit MV movement each cycle
    apm_option(s,c,'Q1.dmax',50);
    % MV limits
    apm_option(s,c,'Q1.upper',100);
    apm_option(s,c,'Q1.lower',0);

    % tune CV
    % how fast to reach setpoint
    apm_option(s,c,'TC.tau',10);
    % trajectory type
    apm_option(s,c,'TC.tr_init',2);

    % let optimizer use MV
    apm_option(s,c,'Q1.status',1);
    % include CV in objective function
    apm_option(s,c,'TC.status',1);

    % feedback status (whether we have measurements)
    apm_option(s,c,'Q1.fstatus',0);
    apm_option(s,c,'TC.fstatus',1);

    % web-viewer option, update every second
    apm_option(s,c,'apm.web_plot_freq',1);

    msg = 'initialization complete';
end