o2c = 250e-3; %mM
o2e = 273e-3; %mM
ko2e = 3.4e-6;
ko2c = 3.4e-6;
vo2t = (469.*o2e/ko2e)./(1+o2e/ko2e+o2c/ko2c);
e = 23.36./vo2t;

o2e = 0:0.0001:1000e-3; %mM
vo2t = e.*(469.*o2e/ko2e)./(1+o2e/ko2e+o2c/ko2c);

hold on
plot(o2e,vo2t,'r-');
% plot(o2e,e,'k-');
