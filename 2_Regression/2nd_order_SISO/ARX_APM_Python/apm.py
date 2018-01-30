# Import
import csv
import math
import os
import random
import string
import time
import webbrowser
from contextlib import closing
import sys

# Get Python version
ver = sys.version_info[0]
#print('Version: '+str(ver))
if ver==2:  # Python 2
    import urllib    
else:       # Python 3+
    import urllib.request, urllib.parse, urllib.error
    #import socket

if ver==2:  # Python 2

    def cmd(server, app, aline):
        '''Send a request to the server \n \
           server = address of server \n \
           app      = application name \n \
           aline  = line to send to server \n'''
        try:
            # Web-server URL address
            url_base = string.strip(server) + '/online/apm_line.php'
            app = app.lower()
            app.replace(" ", "")
            params = urllib.urlencode({'p': app, 'a': aline})
            f = urllib.urlopen(url_base, params)
            # Stream solution output
            if(aline=='solve'):
                line = ''
                while True:
                    char = f.read(1)
                    if not char:
                        break
                    elif char == '\n':
                        print(line)
                        line = ''
                    else:
                        line += char
            # Send request to web-server
            response = f.read()
        except:
            response = 'Failed to connect to server'
        return response

    def load_model(server,app,filename):
        '''Load APM model file \n \
           server   = address of server \n \
           app      = application name \n \
           filename = APM file name'''
        # Load APM File
        f = open(filename,'r')
        aline = f.read()
        f.close()
        app = app.lower()
        app.replace(" ","")
        response = cmd(server,app,' '+aline)
        return

    def load_data(server,app,filename):
        '''Load CSV data file \n \
           server   = address of server \n \
           app      = application name \n \
           filename = CSV file name'''
        # Load CSV File
        f = open(filename,'r')
        aline = f.read()
        f.close()
        app = app.lower()
        app.replace(" ","")
        response = cmd(server,app,'csv '+aline)
        return

    def get_ip(server):
        '''Get current IP address \n \
           server   = address of server'''
        # get ip address for web-address lookup
        url_base = string.strip(server) + '/ip.php'
        f = urllib.urlopen(url_base)
        ip = string.strip(f.read())
        return ip

    def apm_t0(server,app,mode):
        '''Retrieve restart file \n \
           server   = address of server \n \
           app      = application name \n \
           mode = {'ss','mpu','rto','sim','est','ctl'} '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address
        app = app.lower()
        app.replace(" ","")
        url = string.strip(server) + '/online/' + ip + '_' + app + '/' + string.strip(mode) + '.t0'
        f = urllib.urlopen(url)
        # Send request to web-server
        solution = f.read()
        return solution

    def get_solution(server,app):
        '''Retrieve solution results\n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address
        app = app.lower()
        app.replace(" ","")
        url = string.strip(server) + '/online/' + ip + '_' + app + '/results.csv'
        f = urllib.urlopen(url)
        # Send request to web-server
        solution = f.read()

        # Write the file
        sol_file = 'solution_' + app + '.csv'
        fh = open(sol_file,'w')
        # possible problem here if file isn't able to open (see MATLAB equivalent)
        fh.write(solution.replace('\r',''))
        fh.close()        

        # Use array package
        from array import array
        # Import CSV file from web server
        with closing(urllib.urlopen(url)) as f:
            reader = csv.reader(f, delimiter=',')
            y={}
            for row in reader:
                if len(row)==2:
                    y[row[0]] = float(row[1])
                else:
                    y[row[0]] = array('f', [float(col) for col in row[1:]])
        # Return solution
        return y


    def get_file(server,app,filename):
        '''Retrieve any file from web-server\n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        try:
            # Web-server URL address
            app = app.lower()
            app.replace(" ","")
            url = string.strip(server) + '/online/' + ip + '_' + app + '/' + filename
            f = urllib.urlopen(url)
            # Send request to web-server
            file = f.read()
            # Write the file
            fh = open(filename,'w')
            fh.write(file.replace('\r',''))
            fh.close()
            return (file)
        except:
            print('Could not retrieve ' + filename + ' from server')
            return []

    def set_option(server,app,name,value):
        '''Load APM option \n \
           server   = address of server \n \
           app      = application name \n \
           name     = {FV,MV,SV,CV}.option \n \
           value    = numeric value of option '''
        aline = 'option %s = %f' %(name,value)
        app = app.lower()
        app.replace(" ","")
        response = cmd(server,app,aline)
        return response

    def web(server,app):
        '''Open APM web viewer in local browser \n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address    
        app = app.lower()
        app.replace(" ","")
        url = string.strip(server) + '/online/' + ip + '_' + app + '/' + ip + '_' + app + '_oper.htm'
        webbrowser.get().open_new_tab(url)
        return url

    def web_var(server,app):
        '''Open APM web viewer in local browser \n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address    
        app = app.lower()
        app.replace(" ","")
        url = string.strip(server) + '/online/' + ip + '_' + app + '/' + ip + '_' + app + '_var.htm'
        webbrowser.get().open_new_tab(url)
        return url
        
    def web_root(server,app):
        '''Open APM root folder \n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address    
        app = app.lower()
        app.replace(" ","")
        url = string.strip(server) + '/online/' + ip + '_' + app + '/'
        webbrowser.get().open_new_tab(url)
        return url

    def classify(server,app,type,aline):
        '''Classify parameter or variable as FV, MV, SV, or CV \n \
           server   = address of server \n \
           app      = application name \n \
           type     = {FV,MV,SV,CV} \n \
           aline    = parameter or variable name '''
        x = 'info' + ' ' +  type + ', ' + aline
        app = app.lower()
        app.replace(" ","")
        response = cmd(server,app,x)
        return response


    def csv_data(filename):
        '''Load CSV File into Python
           A = csv_data(filename)

           Function csv_data extracts data from a comma
           separated value (csv) file and returns it
           to the array A'''
        try:
            f = open(filename, 'rb')
            reader = csv.reader(f)
            headers = reader.next()
            c = [float] * (len(headers))
            A = {}
            for h in headers:
                A[h] = []
            for row in reader:
                for h, v, conv in zip(headers, row, c):
                    A[h].append(conv(v))
        except ValueError:
            A = {}
        return A

    def csv_lookup(name,replay):
        '''Lookup Index of CSV Column \n \
           name     = parameter or variable name \n \
           replay   = csv replay data to search'''
        header = replay[0]
        try:
            i = header.index(string.strip(name))
        except ValueError:
            i = -1 # no match
        return i

    def csv_element(name,row,replay):
        '''Retrieve CSV Element \n \
           name     = parameter or variable name \n \
           row      = row of csv file \n \
           replay   = csv replay data to search'''
        # get row number
        if (row>len(replay)): row = len(replay)-1
        # get column number
        col = csv_lookup(name,replay)
        if (col>=0): value = float(replay[row][col])
        else: value = float('nan')
        return value

    def get_attribute(server,app,name):
        '''Retrieve options for FV, MV, SV, or CV \n \
           server   = address of server \n \
           app      = application name \n \
           name     = {FV,MV,SV,CV}.{MEAS,MODEL,NEWVAL} \n \n \
             Valid name combinations \n \
            {FV,MV,CV}.MEAS \n \
            {SV,CV}.MODEL \n \
            {FV,MV}.NEWVAL '''
        # Web-server URL address
        url_base = string.strip(server) + '/online/get_tag.php'
        app = app.lower()
        app.replace(" ","")
        params = urllib.urlencode({'p':app,'n':name})
        f = urllib.urlopen(url_base,params)
        # Send request to web-server
        value = eval(f.read())
        return value

    def load_meas(server,app,name,value):
        '''Transfer measurement to server for FV, MV, or CV \n \
           server   = address of server \n \
           app      = application name \n \
           name     = name of {FV,MV,CV} '''
        # Web-server URL address
        url_base = string.strip(server) + '/online/meas.php'
        app = app.lower()
        app.replace(" ","")
        params = urllib.urlencode({'p':app,'n':name+'.MEAS','v':value})
        f = urllib.urlopen(url_base,params)
        # Send request to web-server
        response = f.read()
        return response

else:       # Python 3+
    
    def cmd(server,app,aline):
        '''Send a request to the server \n \
           server = address of server \n \
           app      = application name \n \
           aline  = line to send to server \n'''
        try:
            # Web-server URL address
            url_base = server.strip() + '/online/apm_line.php'
            app = app.lower()
            app.replace(" ","")
            params = urllib.parse.urlencode({'p':app,'a':aline})
            en_params = params.encode()
            f = urllib.request.urlopen(url_base,en_params)
            # Stream solution output
            if(aline=='solve'):
                line = ''
                while True:
                    en_char = f.read(1)
                    char = en_char.decode()
                    if not char:
                        break
                    elif char == '\n':
                        print(line)
                        line = ''
                    else:
                        line += char
            # Send request to web-server
            en_response = f.read()
            response = en_response.decode()
        except:
            response = 'Failed to connect to server'
        return response

    def load_model(server,app,filename):
        '''Load APM model file \n \
           server   = address of server \n \
           app      = application name \n \
           filename = APM file name'''
        # Load APM File
        f = open(filename,'r')
        aline = f.read()
        f.close()
        app = app.lower()
        app.replace(" ","")
        response = cmd(server,app,' '+aline)
        return

    def load_data(server,app,filename):
        '''Load CSV data file \n \
           server   = address of server \n \
           app      = application name \n \
           filename = CSV file name'''
        # Load CSV File
        f = open(filename,'r')
        aline = f.read()
        f.close()
        app = app.lower()
        app.replace(" ","")
        response = cmd(server,app,'csv '+aline)
        return

    def get_ip(server):
        '''Get current IP address \n \
           server   = address of server'''
        # get ip address for web-address lookup
        url_base = server.strip() + '/ip.php'
        f = urllib.request.urlopen(url_base)
        fip = f.read()
        ip = fip.decode().strip()
        return ip

    def apm_t0(server,app,mode):
        '''Retrieve restart file \n \
           server   = address of server \n \
           app      = application name \n \
           mode = {'ss','mpu','rto','sim','est','ctl'} '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address
        app = app.lower()
        app.replace(" ","")
        url = server.strip() + '/online/' + ip + '_' + app + '/' + mode.strip() + '.t0'
        f = urllib.request.urlopen(url)
        # Send request to web-server
        solution = f.read()
        return solution

    def get_solution(server,app):
        '''Retrieve solution results\n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address
        app = app.lower()
        app.replace(" ","")
        url = server.strip() + '/online/' + ip + '_' + app + '/results.csv'
        f = urllib.request.urlopen(url)
        # Send request to web-server
        solution = f.read()

        # Write the file
        sol_file = 'solution_' + app + '.csv'
        fh = open(sol_file,'w')
        # possible problem here if file isn't able to open (see MATLAB equivalent)
        en_solution = solution.decode().replace('\r','')
        fh.write(en_solution)
        fh.close()        

        # Use array package
        from array import array
        # Import CSV file from web server
        with closing(urllib.request.urlopen(url)) as f:
            fr = f.read()
            de_f = fr.decode()        
            reader = csv.reader(de_f.splitlines(), delimiter=',')
            y={}
            for row in reader:
                if len(row)==2:
                    y[row[0]] = float(row[1])
                else:
                    y[row[0]] = array('f', [float(col) for col in row[1:]])
        # Return solution
        return y


    def get_file(server,app,filename):
        '''Retrieve any file from web-server\n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        try:
            # Web-server URL address
            app = app.lower()
            app.replace(" ","")
            url = server.strip() + '/online/' + ip + '_' + app + '/' + filename
            f = urllib.request.urlopen(url)
            # Send request to web-server
            file = f.read()
            # Write the file
            fh = open(filename,'w')
            en_file = file.decode().replace('\r','')
            fh.write(en_file)
            fh.close()
            return (file)
        except:
            print('Could not retrieve ' + filename + ' from server')
            return []
            

    def set_option(server,app,name,value):
        '''Load APM option \n \
           server   = address of server \n \
           app      = application name \n \
           name     = {FV,MV,SV,CV}.option \n \
           value    = numeric value of option '''
        aline = 'option %s = %f' %(name,value)
        app = app.lower()
        app.replace(" ","")
        response = cmd(server,app,aline)
        return response

    def web(server,app):
        '''Open APM web viewer in local browser \n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address    
        app = app.lower()
        app.replace(" ","")
        url = server.strip() + '/online/' + ip + '_' + app + '/' + ip + '_' + app + '_oper.htm'
        webbrowser.get().open_new_tab(url)
        return url

    def web_var(server,app):
        '''Open APM web viewer in local browser \n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address    
        app = app.lower()
        app.replace(" ","")
        url = server.strip() + '/online/' + ip + '_' + app + '/' + ip + '_' + app + '_var.htm'
        webbrowser.get().open_new_tab(url)
        return url
        
    def web_root(server,app):
        '''Open APM root folder \n \
           server   = address of server \n \
           app      = application name '''
        # Retrieve IP address
        ip = get_ip(server)
        # Web-server URL address    
        app = app.lower()
        app.replace(" ","")
        url = server.strip() + '/online/' + ip + '_' + app + '/'
        webbrowser.get().open_new_tab(url)
        return url

    def classify(server,app,type,aline):
        '''Classify parameter or variable as FV, MV, SV, or CV \n \
           server   = address of server \n \
           app      = application name \n \
           type     = {FV,MV,SV,CV} \n \
           aline    = parameter or variable name '''
        x = 'info' + ' ' +  type + ', ' + aline
        app = app.lower()
        app.replace(" ","")
        response = cmd(server,app,x)
        return response


    def csv_data(filename):
        '''Load CSV File into Python
           A = csv_data(filename)

           Function csv_data extracts data from a comma
           separated value (csv) file and returns it
           to the array A'''
        try:
            f = open(filename, 'rb')
            reader = csv.reader(f)
            headers = next(reader)
            c = [float] * (len(headers))
            A = {}
            for h in headers:
                A[h] = []
            for row in reader:
                for h, v, conv in zip(headers, row, c):
                    A[h].append(conv(v))
        except ValueError:
            A = {}
        return A

    def csv_lookup(name,replay):
        '''Lookup Index of CSV Column \n \
           name     = parameter or variable name \n \
           replay   = csv replay data to search'''
        header = replay[0]
        try:
            i = header.index(name.strip())
        except ValueError:
            i = -1 # no match
        return i

    def csv_element(name,row,replay):
        '''Retrieve CSV Element \n \
           name     = parameter or variable name \n \
           row      = row of csv file \n \
           replay   = csv replay data to search'''
        # get row number
        if (row>len(replay)): row = len(replay)-1
        # get column number
        col = csv_lookup(name,replay)
        if (col>=0): value = float(replay[row][col])
        else: value = float('nan')
        return value

    def get_attribute(server,app,name):
        '''Retrieve options for FV, MV, SV, or CV \n \
           server   = address of server \n \
           app      = application name \n \
           name     = {FV,MV,SV,CV}.{MEAS,MODEL,NEWVAL} \n \n \
             Valid name combinations \n \
            {FV,MV,CV}.MEAS \n \
            {SV,CV}.MODEL \n \
            {FV,MV}.NEWVAL '''
        # Web-server URL address
        url_base = server.strip() + '/online/get_tag.php'
        app = app.lower()
        app.replace(" ","")
        params = urllib.parse.urlencode({'p':app,'n':name})
        params_en = params.encode()
        f = urllib.request.urlopen(url_base,params_en)
        # Send request to web-server
        value = eval(f.read())
        return value

    def load_meas(server,app,name,value):
        '''Transfer measurement to server for FV, MV, or CV \n \
           server   = address of server \n \
           app      = application name \n \
           name     = name of {FV,MV,CV} '''
        # Web-server URL address
        url_base = server.strip() + '/online/meas.php'
        app = app.lower()
        app.replace(" ","")
        params = urllib.parse.urlencode({'p':app,'n':name+'.MEAS','v':value})
        params_en = params.encode()
        f = urllib.request.urlopen(url_base,params_en)
        # Send request to web-server
        response = f.read()
        return response

def solve(app,imode,web_option=False):
    '''
     APM Solver for simulation, estimation, and optimization with both
      static (steady-state) and dynamic models. The dynamic modes can solve
      index 2+ DAEs without numerical differentiation.
     
     y = solve(app,imode,web_option=False)
    
     Function solve uploads the model file (apm) and optionally
       a data file (csv) with the same name to the web-server and performs
       a forward-time stepping integration of ODE or DAE equations
       with the following arguments:
    
      Input:      app = model (apm) and data file (csv) name
                imode = simulation mode {1..7}
                                   steady-state  dynamic  sequential
                        simulate     1             4        7
                        estimate     2             5        8
                        optimize     3             6        9
           web_option = open web-viewer
    
     Output: y.names  = names of all variables
             y.values = tables of values corresponding to y.names
             y.nvar   = number of variables
             y.x      = combined variables and values but variable
                          names may be modified to make them valid
                          characters (e.g. replace '[' with '')
    '''

    # server and application file names
    server = 'http://byu.apmonitor.com'
    app = app.lower()
    app.replace(" ","")
    app_model = app + '.apm'
    app_data =  app + '.csv'

    # randomize the application name
    from random import randint
    app = app + '_' + str(randint(1000,9999))
    
    # clear previous application
    cmd(server,app,'clear all')

    try:
        # load model file
        load_model(server,app,app_model)
    except:
        msg = 'Model file ' + app + '.apm does not exist'
        print(msg)
        return []

    # check if data file exists (optional)
    try:
        # load data file
        load_data(server,app,app_data)
    except:
        # data file is optional
        print('Optional data file ' + app + '.csv does not exist')
        pass
    
    # default options
    # use or don't use web viewer
    if web_option:
        set_option(server,app,'nlc.web',2)
    else:
        set_option(server,app,'nlc.web',0)

    # internal nodes in the collocation (between 2 and 6)
    set_option(server,app,'nlc.nodes',3)
    # sensitivity analysis (default: 0 - off)
    set_option(server,app,'nlc.sensitivity',0)
    # simulation mode (1=ss,  2=mpu, 3=rto)
    #                 (4=sim, 5=est, 6=nlc, 7=sqs)
    set_option(server,app,'nlc.imode',imode)

    # attempt solution
    solver_output = cmd(server,app,'solve')

    # check for successful solution
    status = get_attribute(server,app,'nlc.appstatus')

    if status==1:
        # open web viewer if selected
        if web_option:
            web(server,app)
        # retrieve solution and solution.csv
        z = get_solution(server,app)
        return z
    else:
        print(solver_output)
        print('Error: Did not converge to a solution')
        return []

def sysid(data,ni,nu,ny):
    import numpy as np
    '''
     Identification of linear time-invariant models
     
     y = sysid(data,ni,nu,nu)
    
     Function sysid breaks up data into individual elements including:
       column 0 = time
       column 1-nu = inputs
       column nu+1-nu+ny = outputs
         
      Input:    data = data for the regression
                ni   = number of inputs
                nu   = number of input coefficients
                ny   = number of output coefficients
    
     Output:    returns ypred (predicted outputs)
                sysa.apm is written (model file with identified parameters)
                There is optionally a plot and other output that appears
                when flag "fast" is set to False
    '''

    fast = True  # switch "False" for solution analysis
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


def plotter(y, subplots=1, save=False, filename='solution', format='png'):
    '''
    The plotter will go through each of the variables in the output y and
      create plots for them. The number of vertical subplots can be
      specified and the plots can be saved in the same folder.

    This functionality is dependant on matplotlib, so this library must
      be installed on the computer for the automatic plotter to work.

    The input y should be the output from the apm solution. This can be
      retrieved from the server using the following line of code:
      y = get_solution(server, app)
    '''
    try:
        import matplotlib.pyplot as plt
        var_size = len(y)
        colors = ['r-', 'g-', 'k-', 'b-']
        color_pick = 0
        if subplots > 9:
            subplots = 9
        j = 1
        pltcount = 0
        start = True
        for i in range(var_size):
            if list(y)[i] != 'time' and list(y)[i][:3] != 'slk':
                if j == 1:
                    if start != True:
                        plt.xlabel('time')
                    start = False
                    if save:
                        if pltcount != 0:
                            plt.savefig(filename + str(pltcount) + '.' + format, format=format)
                        pltcount += 1
                    plt.figure()
                else:
                    plt.gca().axes.get_xaxis().set_ticklabels([])
                plt.subplot(100*subplots+10+j)
                plt.plot(y['time'], y[list(y)[i]], colors[color_pick], linewidth=2.0)
                if color_pick == 3:
                    color_pick = 0
                else:
                    color_pick += 1
                plt.ylabel(list(y)[i])
                if subplots == 1:
                    plt.title(list(y)[i])
                if j == subplots or i+2 == var_size:
                    j = 1
                else:
                    j += 1
        plt.xlabel('time')
        if save:
            plt.savefig('plots/' + filename + str(pltcount) + '.' + format, format=format)
        if pltcount <= 20:
            plt.show()
    except ImportError:
        print('Dependent Packages not imported.')
        print('Please install matplotlib package to use plotting features.')
    except:
        print('Graphs not created. Double check that the')
        print('simulation/optimization was succesfull')

# This code adds back compatibility with previous versions

apm = cmd
apm_load = load_model
csv_load = load_data
apm_ip = get_ip
apm_sol = get_solution
apm_get = get_file
apm_option = set_option
apm_web = web
apm_web_var = web_var
apm_web_root = web_root
apm_info = classify
apm_tag = get_attribute
apm_meas = load_meas
apm_solve = solve
