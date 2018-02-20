% Retrieve CSV element by finding the 
%  matching name in the csv data
function result = csv_lookup(name,csv)
   % Initialize value
   result = 0;

   % Size of CSV data
   [rows,cols] = size(csv);

   % Find matching name column in csv data
   match = strcmpi(deblank(name),csv(1,:));
   % Retrieve value
   for i = 1:cols,
      if (match(i)),
         result = i;
      end
   end
