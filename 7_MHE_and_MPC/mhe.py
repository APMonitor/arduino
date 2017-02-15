from apm import *
import numpy as np
s = 'http://byu.apmonitor.com'
b = 'mhe'

def mhe(T_meas,Vin):
    params = np.empty(4)
    # input measurements
    apm_meas(s,b,'TK',T_meas)
    apm_meas(s,b,'Vin',Vin)

    # solve MPC
    output = apm(s,b,'solve')
    #print(output)

    # test for successful solution
    if (apm_tag(s,b,'nlc.appstatus')==1):
        # retrieve the K and tau values

        # option #2 retrieval (apm_tag)
        Kp = apm_tag(s,b,'Kp.Newval')
        tau = apm_tag(s,b,'tau.Newval')
        zeta = apm_tag(s,b,'zeta.Newval')
        TK_ss = apm_tag(s,b,'TK_ss.Newval')
    else:
        # display output for debugging
        print(output)
        # not successful, set default parameters
        Kp = 0.359806899452
        tau = 47.7311112863
        zeta = 1.56206738412
        TK_ss = 300.0
    params[0] = Kp
    params[1] = tau
    params[2] = zeta
    params[3] = TK_ss

    return params


def mhe_init():
    apm(s,b,'clear all')

    # load model and data
    apm_load(s,b,'model.apm')
    csv_load(s,b,'mhe.csv')

    # configure MV / CV
    apm_info(s,b,'FV','Kp')
    apm_info(s,b,'FV','tau')
    apm_info(s,b,'FV','zeta')
    apm_info(s,b,'FV','TK_ss')
    apm_info(s,b,'MV','Vin')
    apm_info(s,b,'CV','TK')

    # dynamic estimation
    apm_option(s,b,'nlc.imode',5)
    apm_option(s,b,'nlc.solver',3)

    # tune FV
    apm_option(s,b,'Kp.dmax',0.05)
    apm_option(s,b,'Kp.lower',0.3)
    apm_option(s,b,'Kp.upper',0.4)
    apm_option(s,b,'tau.dmax',2.0)
    apm_option(s,b,'tau.lower',40.0)
    apm_option(s,b,'tau.upper',60.0)
    apm_option(s,b,'zeta.dmax',0.05)
    apm_option(s,b,'zeta.lower',1.3)
    apm_option(s,b,'zeta.upper',1.7)
    apm_option(s,b,'TK_ss.dmax',1.0)
    apm_option(s,b,'TK_ss.lower',290.0)
    apm_option(s,b,'TK_ss.upper',310.0)
    # turn on FVs as degrees of freedom
    apm_option(s,b,'Kp.status',1)
    apm_option(s,b,'tau.status',1)
    apm_option(s,b,'zeta.status',1)
    apm_option(s,b,'TK_ss.status',1)

    apm_option(s,b,'Kp.fstatus',0)
    apm_option(s,b,'tau.fstatus',0)
    apm_option(s,b,'zeta.fstatus',0)
    apm_option(s,b,'TK_ss.fstatus',0)
    
    # read Vin, don't let optimize use MV
    apm_option(s,b,'Vin.status',0)
    apm_option(s,b,'Vin.fstatus',1)
    # include CV in objective function
    apm_option(s,b,'TK.status',1)
    apm_option(s,b,'TK.fstatus',1)

    # web-viewer option, update every second
    apm_option(s,b,'nlc.web_plot_freq',1)

    msg = 'initialization complete'

    return msg
