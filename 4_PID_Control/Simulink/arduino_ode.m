function dTdt = arduino_ode(time,T,heater)

% mass
m = 4 / 1000; % kg (4 gm)
% heat transfer coefficient
U = 10; % W/m^2-K
% surface area
A = 12 / 100^2; % m^2
% heater input
c = 0.01; % W/(heater input, 0-100)
% heat capacity
Cp = 500.0; % J/kg-K
% ambient temperature
Ta = 23 + 273.15; % K

% Stefan-Boltzmann constant
sigma = 5.67e-8; % W/m^2-K^4
eps = 0.9; % emisivity

alpha = U * A / (m*Cp);
beta = eps * sigma * A / (m*Cp);
gamma = c / (m*Cp);
delta = alpha + 3 * beta * Ta^3;
%disp(['alpha: ' num2str(alpha)])
%disp(['delta: ' num2str(delta)])
% approximate gain
gain = gamma / delta;
%disp(['Gain: ' num2str(gain)])
% approximate time constant
tau = 1/delta;
%disp(['Time constant: ' num2str(tau)])


% Accumulation = Convective heat + Radiative heat + Heat generated
dTdt = (U*A * (Ta - T) + ...
    sigma * eps * A * (Ta^4 - T^4) + ...
    c * heater) / (m*Cp); 
end