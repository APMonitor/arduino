% APM Web-Interface Command
%
% response = apm(server,app,command)
%
% This function sends a command to the APM server with
%   the following arguments:
%
%   server = address of server
%      app = application name
%  command = instruction or line sent
% 
% Some commands are:
%   solve     : solve the model on the server
%   clear all : clear the application and all files
%   clear apm : clear just the model file (apm)
%   clear csv : clear just the data file (csv)
%   info {FV,MV,SV,CV}, {name} : create interface to variable 
%   ss.t0 {values} : load ss.t0 (restart file)
%   csva {contents} : add contents to the data file (csv)
%   csv {line} : add one line to the data file (csv)  
%   apm {contents} : add to apm file without carriage return
%   {otherwise} : add line to apm file
function response = apm(server,app,aline)

    % Web-server URL base
    url_base = [deblank(server) '/online/apm_line.php'];
    app = lower(deblank(app));
    params = ['?p=' urlencode(app) '&a=' urlencode(aline)];
    url = [url_base params];
    % Send request to web-server
    response = urlread_apm(url);
    
    % remove newline characters from response
    newline = sprintf('\r');
    response = strrep(response,newline,'');
