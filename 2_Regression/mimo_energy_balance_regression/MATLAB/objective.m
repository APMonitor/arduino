% define objective

function obj = objective(p)
    global T1meas T2meas
    % simulate model
    Tp = simulate(p);
    % calculate objective
    obj =  sum(((Tp(:,1)-T1meas)./T1meas).^2) ...
         + sum(((Tp(:,2)-T2meas)./T2meas).^2);
end