function msg = apm_arx(p,m,ny,nu,alpha,beta,gamma,name)

if nargin <= 6,
    error('apm_arx: Input ARX Model')
end
if nargin == 7,
    name = 'arx';
end
if nargin == 8,
    % trim whitespace
    filename = strtrim(name);
    % parse file name and extension
    [path,name,ext] = fileparts(name);
end
filename = [name '.apm'];

% check sizes for alpha
[alpha_ny,alpha_p] = size(alpha);
if (alpha_ny~=ny),
    disp(['input ny: ', num2str(ny)])
    disp(['alpha ny: ', num2str(alpha_ny)])
    error('ARX Size mismatch for alpha')
end
if (alpha_p~=p),
    disp(['input p: ', num2str(p)])
    disp(['alpha p: ', num2str(alpha_p)])
    error('ARX Size mismatch for alpha')
end

% check sizes for beta
[beta_nu,beta_m,beta_p] = size(beta);
if (beta_m~=m),
    disp(['input m: ', num2str(m)])
    disp(['beta m: ', num2str(beta_m)])
    error('ARX Size mismatch for beta')
end
if (beta_nu~=nu),
    disp(['input nu: ', num2str(nu)])
    disp(['beta nu: ', num2str(beta_nu)])
    error('ARX Size mismatch for beta')
end
if (beta_p~=p),
    disp(['input p: ', num2str(p)])
    disp(['beta p: ', num2str(beta_p)])
    error('ARX Size mismatch for alpha')
end

fid = fopen(filename,'w');
fprintf( fid,'\n');
fprintf( fid,'Objects \n');
fprintf( fid,['  ' name ' = arx\n']);
fprintf( fid,'End Objects \n');
fprintf( fid,'\n');
fprintf( fid,'Connections\n');
fprintf( fid,['  u[1:%d] = ' name '.u[1:%d]\n'],m,m);
fprintf( fid,['  y[1:%d] = ' name '.y[1:%d]\n'],p,p);
fprintf( fid,'End Connections\n');
fprintf( fid,'\n');
fprintf( fid,'Model \n');
fprintf( fid,'  Parameters \n');
if (m==1)
    fprintf( fid,'    u = 0\n');
else
    fprintf( fid,'    u[1:%d] = 0\n',m);
end
fprintf( fid,'  End Parameters \n');
fprintf( fid,'\n');
fprintf( fid,'  Variables \n');
if (p==1)
    fprintf( fid,'    y = 0\n');
else
    fprintf( fid,'    y[1:%d] = 0\n',p);
end
fprintf( fid,'  End Variables \n');
fprintf( fid,'\n');
fprintf( fid,'  Equations \n');
fprintf( fid,'    ! add any additional equations here \n');
fprintf( fid,'  End Equations \n');
fprintf( fid,'End Model \n');
fprintf( fid,'\n');
fprintf( fid,['File ' name '.txt\n']);
fprintf( fid,'  %d      ! m=number of inputs\n',m);
fprintf( fid,'  %d      ! p=number of outputs\n',p);
fprintf( fid,'  %d      ! nu=number of input terms\n',nu);
fprintf( fid,'  %d      ! ny=number of output terms\n',ny);
fprintf( fid,'End File\n');
fprintf( fid,'\n');
fprintf( fid,'! Alpha matrix (ny x p)\n');
fprintf( fid,['File ' name '.alpha.txt \n']);
for i = 1:ny
    for j = 1:p
        fprintf( fid,'  ');
        if j<=p-1
            fprintf( fid,'%d , ', alpha(i,j));
        else
            fprintf( fid,'%d ', alpha(i,j)); % no comma
        end
    end
    fprintf( fid,'\n');
end
fprintf( fid,'End File \n');
fprintf( fid,'\n');
fprintf( fid,'! Beta matrix (p x (nu x m))\n');
fprintf( fid,['File ' name '.beta.txt \n']);
for i = 1:p
    for j = 1:nu
        fprintf( fid,'  ');
        for k = 1:m
            if k<=m-1
                fprintf( fid,'%d , ', beta(j,k,i));
            else
                fprintf( fid,'%d ', beta(j,k,i));
            end
        end
        fprintf( fid,'\n');
    end
end
fprintf( fid,'End File \n');
fprintf( fid,'\n');
fprintf( fid,'! Gamma vector (p x 1)\n');
fprintf( fid,['File ' name '.gamma.txt \n']);
for i = 1:p
    fprintf( fid,'%d ', gamma(i));
    fprintf( fid,'\n');
end
fprintf( fid,'End File \n');
fclose(fid);

msg = ['Created ARX (Auto-Regressive eXogenous inputs) Model: ' filename];

end