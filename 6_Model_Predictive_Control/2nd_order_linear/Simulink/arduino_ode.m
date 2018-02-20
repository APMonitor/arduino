function dTdt = arduino_ode(time,T,heater)

% mass
m = 0.001; % kg (2 gm)
% heat transfer coefficient
h = 200; % W/m^2-K
% surface area
A = 2 / 100^2; % m^2
% heater input
alpha = 0.022; % W/(heater input)
% heat capacity
Cp = 4900.0; % J/kg-K

% approximate time constant
%tau = m*Cp/(h*A);
%disp(['Time constant: ' num2str(tau)])

% ambient temperature
Ta = 23 + 273.15; % K
heater = 100;
dTdt = (h*A * (Ta - T) + alpha * heater) / (m*Cp); 

end