% APM Index 2+ DAE Integrator
% 
% y = apm_solve(app)
%
% Function apm_solve uploads the model file (apm) and optionally
%   a data file (csv) with the same name to the web-server and performs
%   a forward-time stepping integration of ODE or DAE equations
%   with the following arguments:
%
%  Input:      app = model (apm) and data file (csv) name
%
% Output: y.names  = names of all variables
%         y.values = tables of values corresponding to y.names
%         y.nvar   = number of variables
%         y.x      = combined variables and values but variable
%                      names may be modified to make them valid MATLAB
%                      characters (e.g. replace '[' with '_')
% 
function y = apm_solve(app)
    % server and application file names
    server = 'http://xps.apmonitor.com';
    app_model = [app '.apm'];
    app_data = [app '.csv'];
    
    % clear previous application
    apm(server,app,'clear all');

    % check that model file exists (required)
    if (~exist(app_model,'file')),
        disp(['Error: file ' app_model ' does not exist']);
        y = [];
        return
    else
        % load model file
        apm_load(server,app,app_model);
    end

    % check if data file exists (optional)
    if (exist(app_data,'file')),
        % load data file
        csv_load(server,app,app_data);
    end
    
    % default options
    % use or don't use web viewer
    web = false;
    if web,
        apm_option(server,app,'nlc.web',2);
    else
        apm_option(server,app,'nlc.web',0);
    end        
    % internal nodes in the collocation (between 2 and 6)
    apm_option(server,app,'nlc.nodes',3);
    % sensitivity analysis (default: 0 - off)
    apm_option(server,app,'nlc.sensitivity',0);
    % simulation mode (1=ss,  2=mpu, 3=rto)
    %                 (4=sim, 5=est, 6=nlc, 7=sqs)
    apm_option(server,app,'nlc.imode',7);

    % attempt solution
    solver_output = apm(server,app,'solve');

    % check for successful solution
    status = apm_tag(server,app,'nlc.appstatus');

    if status==1,
        % open web viewer if selected
        if web,
            apm_web(server,app);
        end
        % retrieve solution and solution.csv
        y = apm_sol(server,app);
        return
    else
        apm_web_root(server,app);
        disp(solver_output);
        disp('Error: Did not converge to a solution');
        y = solver_output;
        return
    end