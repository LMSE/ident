function vflux = fluxATPS4r(model)

vatps4r = find(strcmpi(model.rxns,'ATPS4r'));
hc = strcmpi(model.mets,'h[c]');
he = strcmpi(model.mets,'h[e]');

sbid = S(:,Vind(irxn))<0;
prid = S(:,Vind(irxn))>0;   

kfwd = pvec.kcat_fwd;
kbkw = pvec.kcat_bkw;
K = pvec.K;

vflux(vatps4r) = kfwd(vatps4r)

