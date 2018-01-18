function TC = arduino_sim(heater)

persistent T0 icount

if (isempty(icount)),
    % set initial conditions
    Ti1 = 23 + 273.15;
    Ti2 = 23 + 273.15;
    T0 = [Ti1;Ti2];
    icount = 0;
end

% increment counter
icount = icount + 1;
time = [0,1];
Q1 = heater(1);
Q2 = heater(2);
[time,T] = ode45(@(t,x)arduino_ode(t,x,Q1,Q2),time,T0);
TK1 = T(end,1);
TK2 = T(end,2);
TK = [TK1;TK2];
T0 = TK;
TC = TK - 273.15;

end
