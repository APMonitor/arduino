% Parse line with delimiter "delim" and return
%   the delimited pieces in the reponse "parts"
function parts = parse(str,delim)
   splitlen = length(delim);
   parts = {};
   while 1
      k = strfind(str, delim);
      if isempty(k)
         parts{end+1} = str;
         break
      end
      parts{end+1} = str(1 : k(1)-1);
      str = str(k(1)+splitlen : end);
   end