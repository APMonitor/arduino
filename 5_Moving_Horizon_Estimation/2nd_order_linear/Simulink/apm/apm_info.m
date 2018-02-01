% APM Variable Classification
% class = FV, MV, SV, CV
%   F or FV = Fixed value - parameter may change to a new value every cycle
%   M or MV = Manipulated variable - independent variable over time horizon
%   S or SV = State variable - model variable for viewing
%   C or CV = Controlled variable - model variable for control
function response = apm_info(server,app,class,name)
   app = lower(deblank(app));
   aline = ['info ' deblank(char(class)) ', ' deblank(char(name))];
   response = apm(server,app,aline);
