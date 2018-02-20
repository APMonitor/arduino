% APM Input Measured Value
%
% response = apm_meas(server,app,name,value)
%
% Function apm_meas sends a measurement to the APM server
%   with the following arguments:
%
%   server = address of server
%      app = application name
%     name = parameter or variable name
%    value = measurement value
%
% A response is returned indicating whether the measurement
%   was successfully recorded
% 
function response = apm_meas(server,app,name,value)

    % Web-server URL base
    app = lower(deblank(app));
    name = strcat(name,'.meas');
    params = ['?p=' urlencode(app) '&n=' urlencode(name) '&v=' urlencode(num2str(value))];
    url = [deblank(server) '/online/meas.php' params];
    
    % Send request to web-server
    response = urlread_apm(url);
