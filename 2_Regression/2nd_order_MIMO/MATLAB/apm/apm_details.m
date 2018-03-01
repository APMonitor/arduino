% APM Report Problem Details
%
% y = apm_details(server,app,x,lam)
%
% This function reports the details of a problem
%   located on the APM server with the following arguments:
%
%   server = address of server
%      app = application name
%        x = values of all variables
%      lam = Lagrange multipliers
%        y = structure with problem information
%
% Reports model details such as values, multipliers, residuals,
%   first derivatives, and second derivatives
%
%      y.nvar  = number of variables
%    y.var.lb  = variable lower bounds
%    y.var.val = variable values
%    y.var.ub  = variable upper bounds
%        y.obj = objective value
%   y.obj_grad = objective gradient
%       y.neqn = number of equations
%     y.eqn.lb = equation lower bounds
%    y.eqn.res = equation residuals
%     y.eqn.ub = equation upper bounds
%        y.jac = jacobian (1st derivatives)
%        y.lam = lagrange multipliers
%    y.hes_obj = second derivative of the objective
% y.hes_eqn{i} = second derivatives of equation {i}
%        y.hes = full Hessian
% 
function y = apm_details(server,app,x,lam)

persistent sol_prev sol_count

% initialize sol_count
if (isempty(sol_count)),
    sol_count = 0;
end

% condition application name
app = lower(deblank(app));

% tolerance for checking if the values are the same
%   as the previous call
tol = 1e-10;

% optionally load solution vector of variables
if (nargin>=3),
    % create 'warm' as a column vector
    if (size(x,1)==1),
        warm = x';
    else
        warm = x;
    end
    
    % see if the values are the same as a previous call
    warm_sum = sum(warm);
    for i = 1:sol_count,
        % check summation of warm first
        if (abs(sol_prev(i).y.sumx-warm_sum) <= tol),
            % check individual elements next
            if (abs(sol_prev(i).y.var.val-warm) <= tol),
                % return previous solution if values haven't changed
                y = sol_prev(i).y;
                return
            end
        end
    end
    
    % load warm.t0 to the server
    fid = fopen('warm.t0','w');
    fprintf(fid,'%20.12e\n',warm);
    fclose(fid);
    
    t0_load(server,app,'warm.t0');
    delete('warm.t0');
end

% optionally load lagrange multipliers to server
if (nargin>=4),
    % create 'lam' as a column vector
    if (size(lam,1)==1),
        lam = lam';
    end
    
    fid = fopen('lam.t0','w');
    fprintf(fid,'%20.12e\n',lam);
    fclose(fid);
    
    t0_load(server,app,'lam.t0');
    delete('lam.t0');
end

% compute details on server
output = apm(server,app,'solve');

% retrieve variables and bounds
apm_get(server,app,'apm_var.txt');
load apm_var.txt
delete('apm_var.txt');
y.nvar = size(apm_var,1); % get number of variables
y.var.lb = apm_var(:,1);
y.var.val = apm_var(:,2);
y.var.ub = apm_var(:,3);

% retrieve objective function value
apm_get(server,app,'apm_obj.txt');
load apm_obj.txt
delete('apm_obj.txt');
y.obj = apm_obj;

% retrieve objective gradient
apm_get(server,app,'apm_obj_grad.txt');
load apm_obj_grad.txt
delete('apm_obj_grad.txt');
y.obj_grad = apm_obj_grad;

% retrieve equation residuals and bounds
apm_get(server,app,'apm_eqn.txt');
load apm_eqn.txt
delete('apm_eqn.txt');
y.neqn = size(apm_eqn,1); % get number of equations
y.eqn.lb = apm_eqn(:,1);
y.eqn.res = apm_eqn(:,2);
y.eqn.ub = apm_eqn(:,3);

% retrieve jacobian
apm_get(server,app,'apm_jac.txt');
load apm_jac.txt
delete('apm_jac.txt');
jac = apm_jac;
y.jac = sparse(jac(:,1),jac(:,2),jac(:,3),y.neqn,y.nvar);

% retrieve lagrange multipliers
apm_get(server,app,'apm_lam.txt');
load apm_lam.txt
delete('apm_lam.txt');
y.lam = apm_lam;

% retrieve hessian of the objective only
apm_get(server,app,'apm_hes_obj.txt');
load apm_hes_obj.txt
delete('apm_hes_obj.txt');
hs = apm_hes_obj;
y.hes_obj = sparse(hs(:,1),hs(:,2),hs(:,3),y.nvar,y.nvar);

% retrieve hessian of the equations only
apm_get(server,app,'apm_hes_eqn.txt');
load apm_hes_eqn.txt
delete('apm_hes_eqn.txt');
hs = apm_hes_eqn;
nhs = size(apm_hes_eqn,1);
i1(1:y.neqn)=0;
i2(1:y.neqn)=0;
% equations listed in sequential order
for i = 1:nhs,
    if(i1(hs(i,1))==0),
        i1(hs(i,1)) = i;
    end
    i2(hs(i,1)) = i;
end
for i = 1:y.neqn,
    if (i1(i)==0),
        y.hes_eqn{i} = sparse(y.nvar,y.nvar);
    else
        y.hes_eqn{i} = sparse(hs(i1(i):i2(i),2),hs(i1(i):i2(i),3),hs(i1(i):i2(i),4),y.nvar,y.nvar);
    end
end

% construct hessian from obj, lam, and eqn portions
y.hes = y.hes_obj;
for i = 1:y.neqn,
    y.hes = y.hes + y.lam(i) * y.hes_eqn{i};
end

% store values
sol_count = sol_count + 1;
sol_prev(sol_count).y = y;
sol_prev(sol_count).y.sumx = sum(y.var.val);