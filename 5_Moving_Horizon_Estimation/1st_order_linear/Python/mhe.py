from APMonitor.apm import *
import numpy as np
s = 'http://byu.apmonitor.com'
#s = 'http://127.0.0.1'
b = 'mhe'

def mhe(T_meas,Q1):
    params = np.empty(4)
    # input measurements
    apm_meas(s,b,'TC',T_meas)
    apm_meas(s,b,'Q1',Q1)

    # solve MPC
    output = apm(s,b,'solve')
    #print(output)

    # test for successful solution
    if (apm_tag(s,b,'nlc.appstatus')==1):
        # retrieve the K and tau values

        # option #2 retrieval (apm_tag)
        Kp = apm_tag(s,b,'Kp.Newval')
        tau = apm_tag(s,b,'tau.Newval')
        TC_ss = apm_tag(s,b,'TC_ss.Newval')
        TC = apm_tag(s,b,'TC.Model')
    else:
        # display output for debugging
        print(output)
        # not successful, set default parameters
        Kp = 0.4
        tau = 160.0
        TC_ss = 23.0
        TC = 23.0
    params[0] = Kp
    params[1] = tau
    params[2] = TC_ss
    params[3] = TC
    
    return params


def mhe_init():
    apm(s,b,'clear all')

    # load model and data
    apm_load(s,b,'model.apm')
    csv_load(s,b,'mhe.csv')

    # configure MV / CV
    apm_info(s,b,'FV','Kp')
    apm_info(s,b,'FV','tau')
    apm_info(s,b,'FV','TC_ss')
    apm_info(s,b,'MV','Q1')
    apm_info(s,b,'CV','TC')

    # dynamic estimation
    apm_option(s,b,'nlc.imode',5)
    apm_option(s,b,'nlc.solver',3)

    # tune FV
    apm_option(s,b,'Kp.dmax',0.05)
    apm_option(s,b,'Kp.lower',0.3)
    apm_option(s,b,'Kp.upper',0.6)
    apm_option(s,b,'tau.dmax',2.0)
    apm_option(s,b,'tau.lower',100.0)
    apm_option(s,b,'tau.upper',200.0)
    apm_option(s,b,'TC_ss.dmax',1.0)
    apm_option(s,b,'TC_ss.lower',22.0)
    apm_option(s,b,'TC_ss.upper',25.0)
    # turn on FVs as degrees of freedom
    apm_option(s,b,'Kp.status',1)
    apm_option(s,b,'tau.status',1)
    apm_option(s,b,'TC_ss.status',1)

    apm_option(s,b,'Kp.fstatus',0)
    apm_option(s,b,'tau.fstatus',0)
    apm_option(s,b,'TC_ss.fstatus',0)
    
    # read Q, don't let optimize use MV
    apm_option(s,b,'Q1.status',0)
    apm_option(s,b,'Q1.fstatus',1)
    # include CV in objective function
    apm_option(s,b,'TC.status',1)
    apm_option(s,b,'TC.fstatus',1)

    # web-viewer option, update every second
    apm_option(s,b,'nlc.web_plot_freq',2)

    msg = 'initialization complete'

    return msg
