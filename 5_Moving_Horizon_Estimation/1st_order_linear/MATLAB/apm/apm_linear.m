function msg = apm_linear(A,b,type,name)

filename = [name '.apm'];    

% extract A, b in sparse form
[mA,nA] = size(A);
if isempty(b),
    b = zeros(mA,1);
    mB = mA;
else
    if size(b,1)==1,
        b = b';
    end
    [mB,nB] = size(b);
end
if (mA~=mB),
    error('Rows of A and b must agree');
end
% convert to sparse form
[ai,aj,av] = find(sparse(A));
a = [ai,aj,av]';
[bi,bj,bv] = find(sparse(b));
b = [bi,bj,bv]';
if(size(b,2)==0),
    b = [1,1,0]';
end
br = [b(1,:); b(3,:)];

fid = fopen(filename,'w');
fprintf( fid,'\n');
fprintf( fid,'Objects \n');
fprintf( fid,['  ' name ' = axb\n']);
fprintf( fid,'End Objects \n');
fprintf( fid,'\n');
fprintf( fid,'Connections\n');
fprintf( fid,['  x[1:%d] = ' name '.x[1:%d]\n'],nA,nA);
fprintf( fid,'End Connections\n');
fprintf( fid,'\n');
fprintf( fid,'Model \n');
fprintf( fid,'  Variables \n');
fprintf( fid,'    x[1:%d] = 0\n',nA);
fprintf( fid,'  End Variables \n');
fprintf( fid,'\n');
fprintf( fid,'  Equations \n');
fprintf( fid,'    ! add any additional equations here \n');
fprintf( fid,'  End Equations \n');
fprintf( fid,'End Model \n');
fprintf( fid,'\n');
fprintf( fid,['File ' name '.txt\n']);
form = ['Ax' strtrim(type) 'b'];
fprintf( fid,['  sparse, ' form '  ! dense or sparse, Ax=b or Ax<b or Ax>b\n']);
fprintf( fid,'  %d      ! m=number of rows in A and b \n',mA);
fprintf( fid,'  %d      ! n=number of columns in A or variables x\n',nA);
fprintf( fid,'End File\n');
fprintf( fid,'\n');
fprintf( fid,['File ' name '.a.txt \n']);
fprintf( fid,'   %d %d %f\n', a );
fprintf( fid,'End File \n');
fprintf( fid,'\n');
fprintf( fid,['File ' name '.b.txt \n']);
fprintf( fid,'   %d %f\n', br );
fprintf( fid,'End File \n');
fclose(fid);

msg = ['Created Linear (Axb) Model: ' filename];

end