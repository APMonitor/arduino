% APM Load Application
%
% app = apm_app(server,name)
%
% Function apm_app loads a model file (apm) and optionally
%   a data file (csv) to the APM server with the 
%   following arguments:
%
%      app = application name
%   server = address of server
%     name = loads name.apm and name.csv
% 
function [app] = apm_app(server,name)

% model name with .apm extension
app_model = [name '.apm'];

% data file with .csv extension (optional)
app_data = [name '.csv'];

% application name, use random number to avoid ip conflicts
app = [name '_' int2str(rand()*10000)];
app = lower(deblank(app));

% clear previous application
apm(server,app,'clear all');

% check that model file exists (required)
if (~exist(app_model,'file')),
    disp(['Error: file ' app_model ' does not exist']);
    app = [];
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
   