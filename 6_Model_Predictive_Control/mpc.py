from apm import *
s = 'http://byu.apmonitor.com'
c = 'hedengren_mpc'

def mpc(T_meas):    
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
    apm_load(s,c,'sysa.apm')
    csv_load(s,c,'control.csv')

    # configure MV / CV
    apm_info(s,c,'MV','Vin')
    apm_info(s,c,'CV','TK')

    # dynamic control
    apm_option(s,c,'nlc.imode',6)
    apm_option(s,c,'nlc.solver',3)
    apm_option(s,c,'nlc.hist_hor',600)

    # tune MV
    # delta MV movement penalty
    apm_option(s,c,'Vin.dcost',1.0e-4)
    # penalize voltage use (energy savings)
    apm_option(s,c,'Vin.cost',0.0)
    # limit MV movement each cycle
    apm_option(s,c,'Vin.dmax',300)
    # MV limits
    apm_option(s,c,'Vin.upper',255)
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

    # web-viewer option, update every second
    apm_option(s,c,'nlc.web_plot_freq',1)
    apm_web(s,c)

    msg = 'initialization complete'

    return msg
