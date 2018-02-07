function y = apm_linprog(f,A,b,Aeq,beq,lb,ub,x0)
%apm_linprog Linear programming.
%   y = apm_linprog(f,A,b,Aeq,beq,LB,UB,X0) writes a linear
%   programming model in APMonitor Modeling Language and attempts
%   to solve the linear programming problem:
%
%            min f'*x   subject to:  A*x <= b, Aeq*x = beq
%             x
%
%   lb and ub are a set of lower and upper bounds on the design variables,
%   x, so that the solution is in the range lb <= x <= ub. Use empty
%   matrices for any of the arguments. Set lb(i) = -1e20 if x(i) has no
%   lower limit and set ub(i) = 1e20 if x(i) has no upper limit. x0 is
%   the initial guess and starting point to x. This is similar to the
%   Matlab linprog solver but uses different solvers such as IPOPT,
%   APOPT, and BPOPT to solve the LP. Additional nonlinear constraints
%   can be added to the lp.apm model for nonlinear programming solution
%   with support for possible mixed-integer variables.
%
%   The solution is returned in the structure y with y.names (variable
%   names), y.values (variable values), y.nvar (number of variables),
%   and y.x (a structure containing each variable and value).
%
%   Example usage is below:
%
% clear all; close all; clc
% addpath('apm')
% 
% % example Linear program
% f = [-5; -4; -6];
% A =  [1 -1  1
%       3  2  4
%       3  2  0];
% b = [20; 42; 30];
% Aeq = [];
% beq = [];
% lb = zeros(3,1);
% ub = [];
% x0 = [];
% 
% % generate and solve APMonitor LP model
% y1 = apm_linprog(f,A,b,Aeq,beq,lb,ub,x0);
% 
% % compare solution to linprog (MATLAB)
% y2 = linprog(f,A,b,Aeq,beq,lb,ub,x0);
% 
% disp('Validate Results with MATLAB linprog')
% for i = 1:max(size(f)),
%     disp(['x[' int2str(i) ']: ' num2str(y1.values(i)) ' = ' num2str(y2(i))])
% end


%% filename to write
filename = ['lp.apm'];

% extract f in sparse form
if ~isempty(f),
    nf = max(size(f));
    if size(f,1)==1,
        f = f';
    end
    H = zeros(1,1);
    
    % convert to sparse form
    [hi,hj,hv] = find(sparse(H));
    h = [hi,hj,hv]';
    [fi,fj,fv] = find(sparse(f));
    f = [fi,fj,fv]';
    if(size(f,2)==0),
        f = [1,1,0]';
    end
    fr = [f(1,:); f(3,:)];
end

% extract A and b in sparse form
if ~isempty(A),
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
    if (mA==1),
        a = [ai;aj;av];
    else
        a = [ai,aj,av]';
    end
    [bi,bj,bv] = find(sparse(b));
    b = [bi,bj,bv]';
    if(size(b,2)==0),
        b = [1,1,0]';
    end
    br = [b(1,:); b(3,:)];
end

% extract Aeq and beq in sparse form
if ~isempty(Aeq),
    [mAeq,nAeq] = size(Aeq);
    if isempty(beq),
        beq = zeros(mAeq,1);
        mBeq = mAeq;
    else
        if size(beq,1)==1,
            beq = beq';
        end
        [mBeq,nBeq] = size(beq);
    end
    if (mAeq~=mBeq),
        error('Rows of Aeq and beq must agree');
    end
    
    % convert to sparse form
    [aeqi,aeqj,aeqv] = find(sparse(Aeq));
    if (mAeq==1),
        aeq = [aeqi;aeqj;aeqv];
    else
        aeq = [aeqi,aeqj,aeqv]';
    end
    [beqi,beqj,beqv] = find(sparse(beq));
    beq = [beqi,beqj,beqv]';
    if(size(beq,2)==0),
        beq = [1,1,0]';
    end
    beqr = [beq(1,:); beq(3,:)];
end

disp('Creating Linear Programming Model lp.apm');
fid = fopen(filename,'w');
fprintf( fid,'\n');
fprintf( fid,'Objects \n');
if ~isempty(f),
    fprintf( fid,[' h = qobj\n']);
end
if ~isempty(A),
    fprintf( fid,[' a = axb\n']);
end
if ~isempty(Aeq),
    fprintf( fid,[' aeq = axb\n']);
end
fprintf( fid,'End Objects \n');
fprintf( fid,'\n');
fprintf( fid,'Connections\n');
sz = -1;
if ~isempty(f),
    fprintf( fid,['  x[1:%d] = h.x[1:%d]\n'],nf,nf);
    sz = nf;
end
if ~isempty(A),
    fprintf( fid,['  x[1:%d] = a.x[1:%d]\n'],nA,nA);
    if (sz>=0),
        if (nA~=sz),
            error('Variables in Ax < b model must be consistent');
        end
    end
end
if ~isempty(Aeq),
    fprintf( fid,['  x[1:%d] = aeq.x[1:%d]\n'],nAeq,nAeq);
    if (sz>=0),
        if (nAeq~=sz),
            error('Variables in Ax = b model must be consistent');
        end
    end
end
fprintf( fid,'End Connections\n');
fprintf( fid,'\n');
fprintf( fid,'Model \n');
fprintf( fid,'  Variables \n');
if (isempty(x0)&&isempty(lb)&&isempty(ub)),
    % default initial conditions
    fprintf( fid,'    x[1:%d] = 0\n',nH);
else
    % create default values
    if (isempty(x0)),
        x0 = zeros(nf,1);
    end
    if (isempty(lb)),
        lb = -1e10 * ones(nf,1);
    end
    if (isempty(ub)),
        ub = 1e10 * ones(nf,1);
    end
    % generate initial conditions and bounds
    for i = 1:nf,
        fprintf( fid,'    x[%i] > %d = %d < %d\n',i,lb(i),x0(i),ub(i));
    end
end
fprintf( fid,'  End Variables \n');
fprintf( fid,'\n');
fprintf( fid,'  Equations \n');
fprintf( fid,'    ! add any additional equations here \n');
fprintf( fid,'  End Equations \n');
fprintf( fid,'End Model \n');
fprintf( fid,'\n');

if ~isempty(f),
    fprintf( fid,'\n');
    fprintf( fid,['File h.txt\n']);
    fprintf( fid,['  sparse, minimize  ! dense or sparse, minimize or maximize\n']);
    fprintf( fid,'  %d      ! n=number of variables \n',nf);
    fprintf( fid,'End File\n');
    fprintf( fid,'\n');
    fprintf( fid,'File h.a.txt \n');
    fprintf( fid,' 1 1 0\n');
    fprintf( fid,'End File \n');
    fprintf( fid,'\n');
    fprintf( fid,['File h.b.txt \n']);
    fprintf( fid,'   %d %f\n', fr );
    fprintf( fid,'End File \n');
end

if ~isempty(A),
    fprintf( fid,'\n');
    fprintf( fid,['File a.txt\n']);
    fprintf( fid,['  sparse, Ax<b \n']);
    fprintf( fid,'  %d      ! m=number of rows in A and b \n',mA);
    fprintf( fid,'  %d      ! n=number of columns in A or variables x\n',nA);
    fprintf( fid,'End File\n');
    fprintf( fid,'\n');
    fprintf( fid,['File a.a.txt \n']);
    fprintf( fid,'   %d %d %f\n', a );
    fprintf( fid,'End File \n');
    fprintf( fid,'\n');
    fprintf( fid,['File a.b.txt \n']);
    fprintf( fid,'   %d %f\n', br );
    fprintf( fid,'End File \n');
end

if ~isempty(Aeq),
    fprintf( fid,'\n');
    fprintf( fid,['File aeq.txt\n']);
    fprintf( fid,['  sparse, Ax=b \n']);
    fprintf( fid,'  %d      ! m=number of rows in A and b \n',mAeq);
    fprintf( fid,'  %d      ! n=number of columns in A or variables x\n',nAeq);
    fprintf( fid,'End File\n');
    fprintf( fid,'\n');
    fprintf( fid,['File aeq.a.txt \n']);
    fprintf( fid,'   %d %d %f\n', aeq );
    fprintf( fid,'End File \n');
    fprintf( fid,'\n');
    fprintf( fid,['File aeq.b.txt \n']);
    fprintf( fid,'   %d %f\n', beqr );
    fprintf( fid,'End File \n');
end
fclose(fid);

disp('Solving Linear Programming Model lp.apm');
s = 'http://xps.apmonitor.com';
a = 'lp';
apm(s,a,'clear all');
apm_load(s,a,'lp.apm');
% select solver (1=APOPT,2=BPOPT,3=IPOPT)
apm_option(s,a,'nlc.solver',3);
output = apm(s,a,'solve');
disp(output);

% return solution
y = apm_sol(s,a);

end