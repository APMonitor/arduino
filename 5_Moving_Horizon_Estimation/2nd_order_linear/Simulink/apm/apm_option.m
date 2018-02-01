% APM Specify Options
%
% response = apm_option(server,app,name,value)
%
% Function apm_option sends an option specification 
%   to the APM server with the following arguments:
%
%   server = address of server
%      app = application name
%     name = option name
%    value = option value
%
% A response is returned indicating whether the option
%   was successfully recorded
%
% Either global options (NLC.option_name) or parameter/variable
%   options (NAME.option_name) are able to be specified with this 
%   function. A full list of available options with their default 
%   values are available here:
%
% Global Options:
%    http://apmonitor.com/wiki/index.php/Main/DbsGlobal
%    
% Variable Options:
%    http://apmonitor.com/wiki/index.php/Main/DbsVariable
% 
function response = apm_option(server,app,name,value)
   app = lower(deblank(app));
   aline = ['option ' deblank(char(name)) ' = ' num2str(value)];
   response = apm(server,app,aline);

