% APM Open Web Page with Variable Values
%
% stat = apm_web_var(server,app)
%
% Function apm_web_var opens the default web-browser
%   and loads a table of variable values 
%
%   server = address of server
%      app = application name
%     stat = message returned when opening browser
% 
function [stat] = apm_web_var(server,app)
   % get ip address for web-address lookup
   ip = deblank(urlread_apm([deblank(server) '/ip.php']));
   app = lower(deblank(app));
   url = [deblank(server) '/online/' ip '_' app '/' ip '_' app '_var.htm'];

   % load web-interface in default browser
   stat = web(url,'-browser');  % doesn't work in some older MATLAB versions

   % display web address and allow the user to click to open
   %%disp(['<a href = "' url '">--- Launch APM Web Interface ---</a>'])
   %%disp([' ' url])