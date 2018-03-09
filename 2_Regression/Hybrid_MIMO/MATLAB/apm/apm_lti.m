function msg = apm_lti(sys,name)

if nargin < 1,
    error('Input State Space or Transfer Function Model')
end
if nargin == 1,
    name = 'sys';
end
if nargin == 2,
    % trim whitespace
    filename = strtrim(name);
    % parse file name and extension
    [path,name,ext] = fileparts(name);
end
filename = [name '.apm'];

% Convert to state space form
sys = ss(sys);
% Check if discrete
if (sys.Ts>0),
    discrete = true;
else
    discrete = false;
end

% extract A, B, C, D matrices in sparse form
[n,m] = size(sys.B);
[p,m] = size(sys.D);

[ai,aj,av] = find(sparse(sys.A));
a = [ai,aj,av]';
[bi,bj,bv] = find(sparse(sys.B));
b = [bi,bj,bv]';
[ci,cj,cv] = find(sparse(sys.C));
if (size(sys.C,1)==1),
    c = [ci;cj;cv];
else
    c = [ci,cj,cv]';
end
[di,dj,dv] = find(sparse(sys.D));
d = [di,dj,dv]';
if(size(d,2)==0),
    d = [1,1,0]';
end

fid = fopen(filename,'w');
fprintf( fid,'\n');
fprintf( fid,'Objects \n');
fprintf( fid,['  ' name ' = lti\n']);
fprintf( fid,'End Objects \n');
fprintf( fid,'\n');
fprintf( fid,'Connections\n');
fprintf( fid,['  u[1:%d] = ' name '.u[1:%d]\n'],m,m);
fprintf( fid,['  x[1:%d] = ' name '.x[1:%d]\n'],n,n);
fprintf( fid,['  y[1:%d] = ' name '.y[1:%d]\n'],p,p);
fprintf( fid,'End Connections\n');
fprintf( fid,'\n');
fprintf( fid,'Model \n');
fprintf( fid,'  Parameters \n');
fprintf( fid,'    u[1:%d] = 0\n',m);
fprintf( fid,'  End Parameters \n');
fprintf( fid,'\n');
fprintf( fid,'  Variables \n');
fprintf( fid,'    x[1:%d] = 0\n',n);
fprintf( fid,'    y[1:%d] = 0\n',p);
fprintf( fid,'  End Variables \n');
fprintf( fid,'\n');
fprintf( fid,'  Equations \n');
fprintf( fid,'    ! add any additional equations here \n');
fprintf( fid,'  End Equations \n');
fprintf( fid,'End Model \n');
fprintf( fid,'\n');
fprintf( fid,'! dimensions\n');
fprintf( fid,'! (nx1) = (nxn)*(nx1) + (nxm)*(mx1)\n');
fprintf( fid,'! (px1) = (pxn)*(nx1) + (pxm)*(mx1)\n');
fprintf( fid,'!\n');
if discrete,
    fprintf( fid,'! discrete form with sampling time = %f\n',sys.Ts);
    fprintf( fid,'! x[k+1] = A * x[k] + B * u[k]\n');
    fprintf( fid,'!   y[k] = C * x[k] + D * u[k]\n');
else
    fprintf( fid,'! continuous form\n');
    fprintf( fid,'! dx/dt = A * x + B * u\n');
    fprintf( fid,'!   y   = C * x + D * u\n');
end
fprintf( fid,['File ' name '.txt\n']);
if discrete,
    fprintf( fid,'  sparse, discrete  ! dense/sparse, continuous/discrete\n');
else
    fprintf( fid,'  sparse, continuous  ! dense/sparse, continuous/discrete\n');
end
fprintf( fid,'  %d      ! m=number of inputs\n',m);
fprintf( fid,'  %d      ! n=number of states\n',n);
fprintf( fid,'  %d      ! p=number of outputs\n',p);
fprintf( fid,'End File\n');
fprintf( fid,'\n');
fprintf( fid,['File ' name '.a.txt \n']);
fprintf( fid,'   %d %d %f\n', a );
fprintf( fid,'End File \n');
fprintf( fid,'\n');
fprintf( fid,['File ' name '.b.txt \n']);
fprintf( fid,'   %d %d %f\n', b );
fprintf( fid,'End File \n');
fprintf( fid,'\n');
fprintf( fid,['File ' name '.c.txt \n']);
fprintf( fid,'   %d %d %f\n', c );
fprintf( fid,'End File \n');
fprintf( fid,'\n');
fprintf( fid,['File ' name '.d.txt \n']);
fprintf( fid,'   %d %d %f\n', d );
fprintf( fid,'End File \n');
fclose(fid);

msg = ['Created Linear Time Invariant (LTI) Model: ' filename];

end