% APM Open Web Viewer in Internet Browser
%
% stat = apm_web(server,app)
%
% Function apm_web opens the default web-browser
%   and loads the application in dashboard view
%   with the following arguments:
%
%   server = address of server
%      app = application name
%     stat = message returned when opening browser
% 
function [stat] = apm_web(server,app)
   % get ip address for web-address lookup
   ip = deblank(urlread_apm([deblank(server) '/ip.php']));
   app = lower(deblank(app));
   
   iapp = [ip '_' app];
   url = [deblank(server) '/online/' iapp '/' iapp '_dashboard.php'];

   % load web-interface in default browser
   stat = web(url,'-browser');  % doesn't work in some older MATLAB versions

   % display web address and allow the user to click to open
   %%disp(['<a href = "' url '">--- Launch APM Web Interface ---</a>'])
   %%disp([' ' url])