function TC = arduino_tclab(heater)

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
    % limit to 0-0.9 (0-100%)
    h1 = @(level) writePWMDutyCycle(a,'D3',max(0,min(100,level))*0.9/100);
    % limit to 0-0.5 (0-100%)
    h2 = @(level) writePWMDutyCycle(a,'D5',max(0,min(100,level))*0.5/100);
end

% increment counter
icount = icount + 1;

% read temperature
TC1 = T1C();
TC2 = T2C();
TC = [TC1,TC2];

% write heater levels
h1(heater(1));
h2(heater(2));

% indicate high temperature with LED
if (TC1 || TC2) > 40
    led(1)
else
    led(0)    
end

end