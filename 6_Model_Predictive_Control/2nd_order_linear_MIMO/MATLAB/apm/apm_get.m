% APM Retrieve File From Server
%
% [] = apm_get(server,app,filename)
%
% Function apm_get retrieves the file from the web-server
%   with the following arguments:
%
%   server = address of server
%      app = application name
% filename = filename to retrieve
%
% A list of all file names that are accessible can be 
%   obtained by issuing the command apm_web_root(server,app)
% 
function [] = apm_get(server,app,filename)
   % get ip address for web-address lookup
   app = lower(deblank(app));
   ip = deblank(urlread_apm([deblank(server) '/ip.php']));    
   url = [deblank(server) '/online/' ip '_' app '/' filename];
   response = urlread_apm(url);
   % write file
   fid = fopen(filename,'w');
   fwrite(fid,response);
   fclose(fid);
