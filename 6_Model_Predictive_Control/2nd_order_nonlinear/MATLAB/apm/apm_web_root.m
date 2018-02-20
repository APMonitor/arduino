% APM Open Web Root Folder in Internet Browser
%
% stat = apm_web_root(server,app)
%
% Function apm_web_root opens the default web-browser
%   and loads a list of files that can be selected for
%   download or viewing
%
%   server = address of server
%      app = application name
%     stat = message returned when opening browser
% 
function [stat] = apm_web_root(server,app)
   % get ip address for web-address lookup
   ip = deblank(urlread_apm([deblank(server) '/ip.php']));
   app = lower(deblank(app));
   url = [deblank(server) '/online/' ip '_' app '/'];

   % load web-interface in default browser
   stat = web(url,'-browser');  % doesn't work in some older MATLAB versions
