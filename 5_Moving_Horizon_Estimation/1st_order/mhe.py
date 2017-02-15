from apm import *
s = 'http://byu.apmonitor.com'
b = 'mhe'

def mhe(T_meas,Vin):
    # input measurements
    apm_meas(s,b,'TdegF',T_meas)
    apm_meas(s,b,'Vin',Vin)

    # solve MPC
    output = apm(s,b,'solve')
    #print(output)

    # test for successful solution
    if (apm_tag(s,b,'nlc.appstatus')==1):
        # retrieve the K and tau values

        # option #2 retrieval (apm_tag)
        K = apm_tag(s,b,'K.Newval')
        tau = apm_tag(s,b,'tau.Newval')
    else:
        # display output for debugging
        print(output)
        # not successful, set voltage to zero
        K = 0.25
        tau = 60.0

    return K,tau


def mhe_init():
    apm(s,b,'clear all')

    # load model and data
    apm_load(s,b,'mhe.apm')
    csv_load(s,b,'mhe.csv')

    # configure MV / CV
    apm_info(s,b,'FV','K')
    apm_info(s,b,'FV','tau')
    apm_info(s,b,'MV','Vin')
    apm_info(s,b,'CV','TDegF')

    # dynamic estimation
    apm_option(s,b,'nlc.imode',5)
    apm_option(s,b,'nlc.solver',3)

    # tune FV
    apm_option(s,b,'K.dmax',0.1)
    apm_option(s,b,'K.lower',0.1)
    apm_option(s,b,'K.upper',0.5)
    apm_option(s,b,'tau.dmax',10.0)
    apm_option(s,b,'tau.lower',100.0)
    apm_option(s,b,'tau.upper',500.0)
    apm_option(s,b,'K.status',1)
    apm_option(s,b,'tau.status',1)
    apm_option(s,b,'K.fstatus',0)
    apm_option(s,b,'tau.fstatus',0)
    
    # read Vin, don't let optimize use MV
    apm_option(s,b,'Vin.status',0)
    apm_option(s,b,'Vin.fstatus',1)
    # include CV in objective function
    apm_option(s,b,'TDegF.status',1)
    apm_option(s,b,'TDegF.fstatus',1)

    # web-viewer option, update every second
    apm_option(s,b,'nlc.web_plot_freq',1)

    msg = 'initialization complete'

    return msg
