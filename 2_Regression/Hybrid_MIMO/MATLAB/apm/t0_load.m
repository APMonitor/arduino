% APM Load T0 File
% File is typically either:
%  Steady State with   ss.t0,  mpu.t0, rto.t0,
%  Dynamic with        sim.t0, est.t0, ctl.t0,
%  Sequential with     sqs.t0
%  Warmstart with      warm.t0
%  Lagrange mult with  lam.t0
function [response] = t0_load(server,app,filename)
   % extract mode by removing .t0
   mode = strrep(filename,'.t0','');
   
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

   % remove newline characters from response
   newline = sprintf('\r');

   % clear any prior file
   url_base = [deblank(server) '/online/apm_t0.php'];
   aline = 'clear';
   params = ['?p=' urlencode(app) '&a=' urlencode(aline) '&f=' urlencode(mode)];
   url = [url_base params];
   response = urlread_apm(url);
   response = strrep(response,newline,'');
   
   % send to server once for every 2000 characters
   ts = size(tline,2);
   block = 2000;
   cycles = ceil(ts/block);
   for i = 1:cycles,
      if i<cycles,
         t0_block = tline((i-1)*block+1:i*block);
      else
         t0_block = tline((i-1)*block+1:end);
      end       
      params = {'p',app,'a',t0_block,'f',mode};
      params = ['?p=' urlencode(app) '&a=' urlencode(t0_block) '&f=' urlencode(mode)];
      response = urlread_apm(url);
      response = strrep(response,newline,'');
   end
   response = 'Successfully loaded T0 file';
   