from apm import *
s = 'http://byu.apmonitor.com'
c = 'mpc'

def mpc(T_meas,params):
    # input new parameter values
    K = params[0]
    tau = params[1]
    zeta = params[2]
    TK_ss = params[3]
    apm_meas(s,c,'Kp',K)
    apm_meas(s,c,'tau',tau)
    apm_meas(s,c,'zeta',zeta)
    apm_meas(s,c,'TK_ss',TK_ss)
    
    # input measurement
    apm_meas(s,c,'TK',T_meas)

    # solve MPC
    output = apm(s,c,'solve')
    #print(output)

    # test for successful solution
    if (apm_tag(s,c,'nlc.appstatus')==1):
        # retrieve the first Vin value
        Vin = apm_tag(s,c,'Vin.Newval')
    else:
        # display output for debugging
        print(output)
        # not successful, set voltage to zero
        Vin = 0

    return Vin


def mpc_init():
    apm(s,c,'clear all')

    # load model and data
    apm_load(s,c,'model.apm')
    csv_load(s,c,'control.csv')

    # configure MV / CV
    apm_info(s,c,'FV','Kp')
    apm_info(s,c,'FV','tau')
    apm_info(s,c,'FV','zeta')
    apm_info(s,c,'FV','TK_ss')
    apm_info(s,c,'MV','Vin')
    apm_info(s,c,'CV','TK')

    # dynamic control
    apm_option(s,c,'nlc.imode',6)
    apm_option(s,c,'nlc.solver',3)
    apm_option(s,c,'nlc.hist_hor',600)

    # tune MV
    # delta MV movement penalty
    apm_option(s,c,'Vin.dcost',0.01)
    # penalize voltage use (energy savings)
    apm_option(s,c,'Vin.cost',0.01)
    # limit MV movement each cycle
    apm_option(s,c,'Vin.dmax',100)
    # MV limits
    apm_option(s,c,'Vin.upper',150)
    apm_option(s,c,'Vin.lower',0)

    # tune CV
    # how fast to reach setpoint
    apm_option(s,c,'TK.tau',10)
    # trajectory type
    apm_option(s,c,'TK.tr_init',2)

    # let optimizer use MV
    apm_option(s,c,'Vin.status',1)
    # include CV in objective function
    apm_option(s,c,'TK.status',1)

    # feedback status (whether we have measurements)
    apm_option(s,c,'Vin.fstatus',0)
    apm_option(s,c,'TK.fstatus',1)
    apm_option(s,c,'Kp.fstatus',1)
    apm_option(s,c,'tau.fstatus',1)
    apm_option(s,c,'zeta.fstatus',1)
    apm_option(s,c,'TK_ss.fstatus',1)

    # web-viewer option, update every second
    apm_option(s,c,'nlc.web_plot_freq',1)

    msg = 'initialization complete'

    return msg
