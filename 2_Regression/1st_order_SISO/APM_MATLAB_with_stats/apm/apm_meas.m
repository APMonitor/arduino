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
    name = strcat(name,'.meas');
    params = {'p',app,'n',name,'v',num2str(value)};
    url = [deblank(server) '/online/meas.php'];
    
    % Send request to web-server
    response = urlread(url,'get',params);
