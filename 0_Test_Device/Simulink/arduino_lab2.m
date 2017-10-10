function TC = arduino_lab2(heater)

persistent icount a

if (isempty(icount))
    % include tclab.m for initialization
    tclab;
    icount = 0;
else
    % voltage read functions
    v1 = @() readVoltage(a, 'A0');
    v2 = @() readVoltage(a, 'A2');
    
    % temperature calculations as a function of voltage for TMP36
    TC = @(V) (V - 0.5)*100.0;          % Celsius
    TK = @(V) TC(V) + 273.15;           % Kelvin
    TF = @(V) TK(V) * 9.0/5.0 - 459.67; % Fahrenhiet
    
    % temperature read functions
    T1C = @() TC(v1());
    T2C = @() TC(v2());
    
    % LED function (0 <= level <= 1)
    led = @(level) writePWMDutyCycle(a,'D9',max(0,min(1,level)));  % ON
    
    % heater output (0 <= heater <= 100)
    % 0 = 0 V and 100 = 5 V
    h1 = @(level) writePWMVoltage(a,'D3',max(0,min(100,level))/20);
    h2 = @(level) writePWMVoltage(a,'D5',max(0,min(100,level))/20);    
end

% increment counter
icount = icount + 1;

% read temperature
TC = T2C();
% write heater
h2(heater);

% indicate high temperature with LED
if TC > 40
    led(1)
else
    led(0)
end

end