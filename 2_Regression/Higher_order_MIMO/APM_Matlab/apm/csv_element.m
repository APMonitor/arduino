% Retrieve CSV element
%
% value = csv_element(name,row,csv)
%
% This function looks up "name" in the cell
%   array "csv" and returns the value in row
%   number "row"
%
function value = csv_element(name,row,csv)
   % Size of CSV data
   [rows,cols] = size(csv);
   % Take last row if beyond max rows
   if (row>rows),
      row = rows-1;
   end
   % get column number
   col = csv_lookup(name,csv);
   if (col>=1),
      value = str2num(csv{row+1,col});
   else
      value = NaN;
   end
