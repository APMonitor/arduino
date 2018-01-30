% Load CSV File into MATLAB
%
% A = csv_data(filename)
%
% Function csv_data extracts data from a comma
%   separated value (csv) file and returns it
%   to the matrix A
% 
function [A] = csv_data(filename)
   % load data from csv file with header
   fid = fopen(filename, 'r');
   aline = fgetl(fid);
   
   % Split header
   A(1,:) = deblank(parse(aline, ','));
   
   % Parse and read rest of file
   ctr = 1;
   while(~feof(fid))
      if ischar(aline) 
         ctr = ctr + 1;
         aline = fgetl(fid); 
         A(ctr,:) = parse(aline, ','); 
      else
         break; 
      end
   end
   fclose(fid);
