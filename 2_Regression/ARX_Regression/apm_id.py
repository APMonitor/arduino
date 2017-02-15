import numpy as np
from apm import *

def apm_id(data,ni,nu,ny):
    fast = False  # switch "False" for solution analysis
    obj_scale = 1
    n = np.size(data,0)
    p = np.size(data,1)
    no = p - ni - 1
    if no<=0:
        print('Data file needs at least 1 column for output data')
        return
    m = max(ny,nu)

    # first column is time
    time = data[:,0].copy()
    dt = time[1] - time[0]

    # inputs are the next column(s)
    u_ss = data[0,1:1+ni].copy()
    u = data[:,1:1+ni].copy()

    # outputs are the final column(s)
    y_ss = data[0,1+ni:1+ni+no].copy()
    y = data[:,1+ni:1+ni+no].copy()

    for i in range(n):
        for j in range(ni):
            u[i,j] = u[i,j] - u_ss[j]
        for j in range(no):
            y[i,j] = y[i,j] - y_ss[j]

    fid = open('myModel.apm','w')
    fid.write('Objects\n')
    fid.write('  sum_a[1:no] = sum(%i)\n'%ny)
    fid.write('  sum_b[1:ni][1::no] = sum(%i)\n'%nu)
    fid.write('End Objects\n')
    fid.write('  \n')
    fid.write('Connections\n')
    fid.write('  a[1:ny][1::no] = sum_a[1::no].x[1:ny]\n')
    fid.write('  b[1:nu][1::ni][1:::no] = sum_b[1::ni][1:::no].x[1:nu]\n')
    fid.write('  sum_a[1:no] = sum_a[1:no].y\n')
    fid.write('  sum_b[1:ni][1::no] = sum_b[1:ni][1::no].y\n')
    fid.write('End Connections\n')
    fid.write('  \n')
    fid.write('Constants\n')
    fid.write('  n = %s\n' %str(n))
    fid.write('  ni = %s\n'%str(ni))
    fid.write('  no = %s\n'%str(no))
    fid.write('  ny = %s\n'%str(ny))
    fid.write('  nu = %s\n'%str(nu))
    fid.write('  m = %s\n'%str(m))
    fid.write('  \n')
    fid.write('Parameters\n')
    fid.write('  a[1:ny][1::no] = 0 !>= -1 <= 1\n')
    fid.write('  b[1:nu][1::ni][1:::no] = 0\n')
    fid.write('  c[1:no] = 0\n')
    fid.write('  u[1:n][1::ni]\n')
    fid.write('  y[1:m][1::no]\n')
    fid.write('  z[1:n][1::no]\n')
    fid.write('  \n')
    fid.write('Variables\n')
    fid.write('  y[m+1:n][1::no] = 0\n')
    fid.write('  sum_a[1:no] = 0 !<= 1\n')
    fid.write('  sum_b[1:ni][1::no] = 0\n')
    fid.write('  K[1:ni][1::no] = 0 !>=0 <= 10 \n') 
    fid.write('  \n')
    fid.write('Equations\n')
    fid.write('  y[m+1:n][1::no] = a[1][1::no]*y[m:n-1][1::no]')
    for j in range(1,ni+1):
        fid.write(' + b[1][%i][1::no]*u[m:n-1][%i]'%(j,j,))
        for i in range(2,nu+1): 
            fid.write(' + b[%i][%i][1::no]*u[m-%i:n-%i][%i]'%(i,j,i-1,i,j,))
    for i in range(2,ny+1): 
        fid.write(' + a[%i][1::no]*y[m-%i:n-%i][1::no]'%(i,i-1,i,))
    fid.write('\n')
    fid.write('  K[1:ni][1::no] * (1 - sum_a[1::no]) = sum_b[1:ni][1::no]\n')
    fid.write('  minimize %e * (y[m+1:n][1::no] - z[m+1:n][1::no])^2\n'%obj_scale)
    fid.close()
    
    fid = open('myData.csv','w')
    for j in range(1,ni+1): 
        for i in range(1,n+1): 
            fid.write('u[%i][%i], %e\n'%(i,j,u[i-1,j-1],))
    for k in range(1,no+1):
        for i in range(1,n+1):
            fid.write('z[%i][%i], %e\n'%(i,k,y[i-1,k-1],))
    for k in range(1,no+1): 
        for i in range(1,n+1): 
            fid.write('y[%i][%i], %e\n'%(i,k,y[i-1,k-1],))
    fid.close()
    
    s = 'http://byu.apmonitor.com'
    #s = 'http://127.0.0.1'
    a = 'apm_id'
    apm(s,a,'clear all')
    apm_load(s,a,'myModel.apm')
    csv_load(s,a,'myData.csv')
    
    apm_option(s,a,'nlc.solver',3)
    apm_option(s,a,'nlc.imode',2)
    apm_option(s,a,'nlc.max_iter',100)
    
    for i in range(1,no+1): 
        name = 'c[' + str(i) + ']'
        apm_info(s,a,'FV',name)
        apm_option(s,a,name+'.status',0)
    for k in range(1,no+1): 
        for i in range(1,ny+1): 
            name = 'a[' + str(i) + '][' + str(k) + ']'
            apm_info(s,a,'FV',name)
            apm_option(s,a,name+'.status',1)
    for k in range(1,no+1): 
        for j in range(1,nu+1): 
            for i in range(1,nu+1): 
                name = 'b[' + str(i) + '][' + str(j) + '][' + str(k) + ']'
                apm_info(s,a,'FV',name)
                apm_option(s,a,name+'.status',1)
    output = apm(s,a,'solve')

    # retrieve and visualize solution
    sol = apm_sol(s,a)
    ypred = np.empty((n,no))
    for j in range(no):
        for i in range(n):
            yn = 'y['+str(i+1)+']['+str(j+1)+']'
            ypred[i,j] = sol[yn]

    if (not fast):
        # open web-viewer
        apm_web(s,a)

        import matplotlib.pyplot as plt
        plt.figure()
        plt.subplot(2,1,1)
        for i in range(ni):
            plt.plot(time,u[:,i]+u_ss[i])
        plt.subplot(2,1,2)
        for i in range(no):
            plt.plot(time,y[:,i]+y_ss[i],'r-')
            plt.plot(time,ypred[:,i]+y_ss[i],'b--')
        plt.show()

    success = apm_tag(s,a,'nlc.appstatus')
    if success==1:
        obj = apm_tag(s,a,'nlc.objfcnval')
        if (not fast):
            print(output)
        print('Successful solution with objective: ' + str(obj))
    else:
        print(output)
        print('Unsuccessful, do not write sysa.apm')
        return

    alpha = np.empty((ny,no))
    beta = np.empty((nu,ni,no))
    gamma = np.empty((no))
    for j in range(1,no+1):
        for i in range(1,ny+1):
            name = 'a['+str(i)+']['+str(j)+']'
            alpha[i-1,j-1] = apm_tag(s,a,name+'.newval');
    for k in range(1,no+1):
        for j in range(1,ni+1):
            for i in range(1,nu+1):
                name = 'b['+str(i)+']['+str(j)+']['+str(k)+']'
                beta[i-1,j-1,k-1] = apm_tag(s,a,name+'.newval')
    for i in range(1,no+1):
        name = 'c['+str(i)+']'
        gamma[i-1] = apm_tag(s,a,name+'.newval')

    name = 'sysa'
    fid = open('sysa.apm','w')
    fid.write('Objects\n')
    fid.write(' '+name+' = arx\n')    
    fid.write('End Objects\n')
    fid.write('\n')    
    fid.write('Connections\n')
    if ni==1:
        fid.write('  u = '+name+'.u\n')
    else:
        fid.write('  u[1:%i] = '%(ni,)+name+'.u[1:%i]\n'%(ni,))
    if no ==1:
        fid.write('  y = '+name+'.y\n')
    else:
        fid.write('  y[1:%i] = '%(no,)+name+'.y[1:%i]\n'%(no,))
    fid.write('End Connections\n')
    fid.write('\n')
    fid.write('Model \n')
    fid.write('  Parameters \n')
    if ni==1:
        fid.write('    u = 0\n')
    else:
        fid.write('    u[1:%i] = 0\n'%(ni,))
    fid.write('  End Parameters \n')
    fid.write('\n')
    fid.write('  Variables \n')
    if no==1:
        fid.write('    y = 0\n')
    else:
        fid.write('    y[1:%i] = 0\n'%(no,))
    fid.write('  End Variables \n')
    fid.write('\n')
    fid.write('  Equations \n')
    fid.write('    ! add any additional equations here \n')
    fid.write('  End Equations \n')
    fid.write('End Model \n')
    fid.write('\n')
    fid.write('File '+name+'.txt\n')
    fid.write('  %i      ! m=number of inputs\n'%(ni,))
    fid.write('  %i      ! p=number of outputs\n'%(no,))
    fid.write('  %i      ! nu=number of input terms\n'%(nu,))
    fid.write('  %i      ! ny=number of output terms\n'%(ny,))
    fid.write('End File\n')
    fid.write('\n')
    fid.write('! Alpha matrix (ny x p)\n')
    fid.write('File '+name+'.alpha.txt \n')
    for i in range(1,ny+1):
        for j in range(1,no+1):
            fid.write('  ')
            if j<=no-1:
                fid.write('%e , '%(alpha[i-1,j-1],))
            else:
                fid.write('%e '%(alpha[i-1,j-1],)) # no comma
        fid.write('\n')
    fid.write('End File \n')
    fid.write('\n')
    fid.write('! Beta matrix (p x (nu x m))\n')
    fid.write('File '+name+'.beta.txt \n')
    for i in range(1,no+1):
        for j in range(1,nu+1):
            fid.write('  ')
            for k in range(1,ni+1):
                if k<=ni-1:
                    fid.write('%e , '%(beta[j-1,k-1,i-1],))
                else:
                    fid.write('%e '%(beta[j-1,k-1,i-1],))
            fid.write('\n')
    fid.write('End File \n')
    fid.write('\n')
    fid.write('! Gamma vector (p x 1)\n')
    fid.write('File '+name+'.gamma.txt \n')
    for i in range(1,no+1):
        fid.write('%e \n'%(gamma[i-1],))
    fid.write('End File \n')
    fid.close()

    msg = 'Created ARX (Auto-Regressive eXogenous inputs) Model: sysa.apm'
    print(msg)

    return ypred+y_ss
