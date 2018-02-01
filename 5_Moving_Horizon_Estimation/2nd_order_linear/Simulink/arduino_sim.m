function TC = arduino_sim(heater)

persistent T0 icount

if (isempty(icount)),
    % set initial condition
    T0 = 23+273.15;
    icount = 0;
end

% increment counter
icount = icount + 1;
time = [0,1];
[time,T] = ode15s(@(t,x)arduino_ode(t,x,heater),time,T0);
TK = T(end);
T0 = TK;

noise = (rand()-0.5)*3.0;
TC = TK - 273.15 + noise;

end
