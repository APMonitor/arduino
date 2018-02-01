% APM Load Data File
%
% response = csv_load(server,app,filename)
%
% Function csv_load uploads the data file (csv) to the web-server
%   with the following arguments:
%
%   server = address of server
%      app = application name
% filename = data filename
%
% A response is returned indicating whether the file was 
%   uploaded successfully to the server
% 
function [response] = csv_load(server,app,filename)
   % convert to lowercase and deblank
   app = lower(deblank(app));

   % load model
   fid=fopen(filename,'r');
   tline = [];
   while 1
      aline = fgets(fid);
      if ~ischar(aline), break, end
      % remove any double quote marks
      aline = [strrep(aline,'"',' ')];
      tline = [tline aline];
   end
   fclose(fid);

   % send to server once for every 2000 characters
   ts = size(tline,2);
   block = 2000;
   cycles = ceil(ts/block);
   for i = 1:cycles,
      if i<cycles,
         csv_block = ['csva ' tline((i-1)*block+1:i*block)];
      else
         csv_block = ['csv ' tline((i-1)*block+1:end)];
      end       
      response = apm(server,app,csv_block);
   end
   response = 'Successfully loaded CSV file';
      
