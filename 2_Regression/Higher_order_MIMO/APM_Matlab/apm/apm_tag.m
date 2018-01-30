% APM Retrieve an Option Value (Tag)
%
% response = apm_tag(server,app,name)
%
% Function apm_tag retrieves an option specification from
%   the APM server with the following arguments:
%
%   server = address of server
%      app = application name
%     name = option name
% response = option value
%
% Either global options (NLC.option_name) or parameter/variable
%   options (NAME.option_name) are able to be retrieved with this 
%   function. A full list of available options with their default 
%   values are available here:
%
% Global Options:
%    http://apmonitor.com/wiki/index.php/Main/DbsGlobal
%    
% Variable Options:
%    http://apmonitor.com/wiki/index.php/Main/DbsVariable
% 
function response = apm_tag(server,app,name)
   app = lower(deblank(app));

    % Web-server URL base
    url_base = [deblank(server) '/online/get_tag.php'];

    % Send request to web-server
    params = ['?p=' urlencode(app) '&n=' urlencode(name)];
    url = [url_base params];
    % Send request to web-server
    response = str2num(urlread_apm(url));
