% Function apm_id for identification of a linear model
% Inputs
%   data = data set with time, inputs, outputs
%   ni = number of inputs (others are outputs)
%   nu = number of input terms (numerator)
%   ny = number of output terms (denominator)
%
% Outputs
%   sysd = discrete transfer function estimated from data
function sysd = apm_id(data,ni,nu,ny)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Configuration
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% include plots and other analysis if it does not need to be fast
fast = false;
obj_scale = 1;

% size of data
[n,p] = size(data);
no = p - ni - 1;
if (no<=0)
    error('Data file needs additional columns for outputs')
end
m = max(ny,nu);

% time
time = data(:,1);
% time step
dt = time(2) - time(1);
% input
u_ss = data(1,2:1+ni);
u = data(:,2:1+ni);
% output
y_ss = data(1,2+ni:1+ni+no);
y = data(:,2+ni:1+ni+no);
for i = 1:size(y,1),
    u(i,:) = u(i,:) - u_ss;
    y(i,:) = y(i,:) - y_ss;
end

%% write model
fid = fopen('myModel.apm','w');
fprintf(fid,'Objects\n');
fprintf(fid,'  sum_a[1:no] = sum(%i)\n',ny);
fprintf(fid,'  sum_b[1:ni][1::no] = sum(%i)\n',nu);
fprintf(fid,'End Objects\n');
fprintf(fid,'  \n');
fprintf(fid,'Connections\n');
fprintf(fid,'  a[1:ny][1::no] = sum_a[1::no].x[1:ny]\n');
fprintf(fid,'  b[1:nu][1::ni][1:::no] = sum_b[1::ni][1:::no].x[1:nu]\n');
fprintf(fid,'  sum_a[1:no] = sum_a[1:no].y\n');
fprintf(fid,'  sum_b[1:ni][1::no] = sum_b[1:ni][1::no].y\n');
fprintf(fid,'End Connections\n');
fprintf(fid,'  \n');
fprintf(fid,'Constants\n');
fprintf(fid,'  n = %s\n',int2str(n));
fprintf(fid,'  ni = %s\n',int2str(ni));
fprintf(fid,'  no = %s\n',int2str(no));
fprintf(fid,'  ny = %s\n',int2str(ny));
fprintf(fid,'  nu = %s\n',int2str(nu));
fprintf(fid,'  m = %s\n',int2str(m));
fprintf(fid,'  \n');
fprintf(fid,'Parameters\n');
fprintf(fid,'  a[1:ny][1::no] = 0 >= -1 <= 1\n');
fprintf(fid,'  b[1:nu][1::ni][1:::no] = 0\n');
fprintf(fid,'  c[1:no] = 0\n');
fprintf(fid,'  u[1:n][1::ni]\n');
fprintf(fid,'  y[1:m][1::no]\n');
fprintf(fid,'  z[1:n][1::no]\n');
fprintf(fid,'  \n');
fprintf(fid,'Variables\n');
fprintf(fid,'  y[m+1:n][1::no] = 0\n');
fprintf(fid,'  sum_a[1:no] = 0 , <= 1\n');
fprintf(fid,'  sum_b[1:ni][1::no] = 0\n');
fprintf(fid,'  K[1:ni][1::no] = 0 >= 0 <= 10\n');
fprintf(fid,'  \n');
fprintf(fid,'Equations\n');
fprintf(fid,'  y[m+1:n][1::no] = a[1][1::no]*y[m:n-1][1::no]');
for j = 1:ni
    fprintf(fid,' + b[1][%i][1::no]*u[m:n-1][%i]',j,j);
    for i = 2:nu
        fprintf(fid, ' + b[%i][%i][1::no]*u[m-%i:n-%i][%i]',i,j,i-1,i,j);
    end
end
for i = 2:ny
    fprintf(fid, ' + a[%i][1::no]*y[m-%i:n-%i][1::no]',i,i-1,i);
end
fprintf(fid,'\n');
%        K(i,j) = sum(beta(:,j,i)) / (1-sum(alpha(:,i)));
fprintf(fid,'  K[1:ni][1::no] * (1 - sum_a[1::no]) = sum_b[1:ni][1::no]\n');
fprintf(fid,'  minimize %12.8f * (y[m+1:n][1::no] - z[m+1:n][1::no])^2\n',obj_scale);
fclose(fid);

%% write data
fid = fopen('myData.csv','w');
for j = 1:ni
    for i = 1:n
        fprintf(fid,'u[%i][%i], %12.8f\n', i,j,u(i,j));
    end
end
for k = 1:no
    for i = 1:n
        fprintf(fid,'z[%i][%i], %12.8f\n', i,k,y(i,k));
    end
end
for k = 1:no
    for i = 1:n
        fprintf(fid,'y[%i][%i], %12.8f\n', i,k,y(i,k));
    end
end
fclose(fid);

%% set up
addpath('apm');
s = 'http://byu.apmonitor.com';
a = 'apm_id';
apm(s,a,'clear all');
apm_load(s,a,'myModel.apm');
csv_load(s,a,'myData.csv');

apm_option(s,a,'nlc.solver',3);
apm_option(s,a,'nlc.imode',2);
apm_option(s,a,'nlc.max_iter',100);

% estimate nominal steady state conditions
%  c = y0 - sum_(i=1)^ny (ai * y0) - sum_(i=1)^nu (bi * u0)
for i = 1:no
    name = ['c[' int2str(i) ']'];
    apm_info(s,a,'FV',name);
    apm_option(s,a,[name '.status'],0);
end

% estimate alphas
for k = 1:no
    for i = 1:ny
        name = ['a[' int2str(i) '][' int2str(k) ']'];
        apm_info(s,a,'FV',name);
        apm_option(s,a,[name '.status'],1);
    end
end
% estimate betas
for k = 1:no
    for j = 1:ni
        for i = 1:nu
            name = ['b[' int2str(i) '][' int2str(j) '][' int2str(k) ']'];
            apm_info(s,a,'FV',name);
            apm_option(s,a,[name '.status'],1);
        end
    end
end
%% solve
output = apm(s,a,'solve');
disp(output);


%% retrieve and visualize solution
sol = apm_sol(s,a);
for j = 1:no
    for i = 1:n
        eval(['ypred(' int2str(i) ',' int2str(j) ') = sol.x.y' int2str(i) int2str(j) ';']);
    end
end
for j = 1:no
    for i = 1:ny
        name = ['a[' int2str(i) '][' int2str(j) ']'];
        alpha(i,j) = apm_tag(s,a,[name '.newval']);
    end
end
for k = 1:no
    for j = 1:ni
        for i = 1:nu
            name = ['b[' int2str(i) '][' int2str(j) '][' int2str(k) ']'];
            beta(i,j,k) = apm_tag(s,a,[name '.newval']);
        end
    end
end
for i = 1:no
    name = ['c[' int2str(i) ']'];  
    gamma(i) = apm_tag(s,a,[name '.newval']);
end

for i = 1:no
    for j = 1:ni
        K(i,j) = sum(beta(:,j,i)) / (1-sum(alpha(:,i)));
    end
end

if (~fast),
    disp('alpha:')
    disp(alpha)
    disp('beta:')
    disp(beta)
    disp('gamma:')
    disp(gamma)
    disp('K')
    disp(K)
    
    % plot results
    figure(1)
    
    subplot(3,1,1)
    plot(time,u(:,1),'r-','LineWidth',2);
    
    subplot(3,1,2)
    plot(time,u(:,2),'k:','LineWidth',2);
    
    subplot(3,1,3)
    plot(time,y,'b--','LineWidth',2);
    hold on
    plot(time,ypred);
    
    apm_web(s,a); 
end

% generate ARX model
apm_arx(no,ni,ny,nu,alpha,beta,gamma,'sysa');

% generate different model forms
% MATLAB doesn't like zero roots
for i = 1:ny,
    for j = 1:no,
        if (abs(alpha(i,j))<1e-5),
            alpha(i,j) = 1e-5;
        end
    end
end
% create LTI model, discrete transfer function
for i = 1:no,
    for j = 1:ni,
        sysd(i,j) = tf([0 beta(:,j,i)'],[1 -alpha(:,i)'],dt,'Variable','z^-1');
    end
end

% generate APMonitor model files (sysc.apm and sysd.apm)
% discrete state space models
apm_lti(sysd,'sysd');
if (~fast)
    % generate continuous state space form
    sysc = d2c(sysd);
    apm_lti(sysd,'sysc');
    figure(2)
    step(sysd,sysc)
end

return