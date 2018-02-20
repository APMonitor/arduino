% APM Load Model File
%
% response = apm_load(server,app,filename)
%
% Function apm_load uploads the model file (apm) to the web-server
%   with the following arguments:
%
%   server = address of server
%      app = application name
% filename = model filename
%
% A response is returned indicating whether the file was 
%   uploaded successfully to the server
% 
function [response] = apm_load(server,app,filename)
   app = lower(deblank(app));
   % load model
   fid=fopen(filename,'r');
   tline = [];
   while 1
      aline = fgets(fid);
      if ~ischar(aline), break, end
      tline = [tline aline];
   end
   fclose(fid);

   % send to server once for every 2000 characters
   ts = size(tline,2);
   block = 2000;
   cycles = ceil(ts/block);
   for i = 1:cycles,
      if i<cycles,
         apm_block = ['apm ' tline((i-1)*block+1:i*block)];
      else
         apm_block = ['apm ' tline((i-1)*block+1:end)];
      end       
      response = apm(server,app,apm_block);
   end
   response = 'Successfully loaded APM file';
   