function sol = IntegrateModel(model,ess_rxn,Vup_struct,ensb,mc,change_pos,change_neg)
%change in initial conditions
if nargin<7
    change_neg = struct([]);
end
if nargin < 6
    change_pos = struct([]);
end
%check if concentrations are initialized
if nargin < 5
    %reinitialize concentrations
    imc = zeros(model.nt_metab,1);
%     imc(strcmpi(model.mets,'pep[c]')) = 0.002;
%     imc(strcmpi(model.mets,'pep[c]')) = 1e-5;
else
    imc = mc;
    imc(strcmpi(model.mets,'glc[e]')) = imc(strcmpi(model.mets,'glc[e]'));
%     imc(strcmpi(model.mets,'q8h2[c]')) = 100;
%     imc(strcmpi(model.mets,'pi[c]')) = 100;
end

if nargin<4
    error('getiest:NoA','No parameter vector');
else
    pvec = ensb{1,2};
end
    
if nargin<3
    Vup_struct([]);
end
if nargin<2
    ess_rxn = {};
end
%initialize solver properties
[model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,1.2);

% model.Vuptake = zeros(model.nt_rxn,1);
% h2o = find(strcmpi(model.rxns,'exH2O'));
% pi =  find(strcmpi(model.rxns,'exPI'));
h = find(strcmpi(model.rxns,'exH'));
% 
model.Vuptake([h]) = [1000];

%noramlize concentration vector to intial state
Nimc = imc./imc;
Nimc(imc==0) = 0;

%intorduce perturbation in initial conditions
% met.glc_e = 10;
% Nimc(strcmpi(model.mets,'glc[e]')) = 1.1;
if ~isempty(change_pos)
    Nimc = changeInitialCondition(model,Nimc,change_pos);
end
if ~isempty(change_neg)
    Nimc = changeInitialCondition(mdoel,Nimc,[],change_neg);
end

model.imc = imc;
model.imc(model.imc==0) = 1;
%calculate initial flux
flux = iflux(model,pvec,Nimc.*imc);
dXdt = ODEmodel(0,Nimc,[],model,pvec);

%add ADMAT and subfolders to bottom of search path
addpath(genpath('C:\Users\shyam\Documents\MATLAB\zz_ADMAT-2.0'),'-end');

% %call to ADmat for stability/jacobian info
[Y,Jac] = stabilityADMAT(model,pvec,Nimc);
e_val = eig(Jac);

rmpath('C:\Users\shyam\Documents\MATLAB\zz_ADMAT-2.0');

%test reals of eigen values of jacobians
if any(real(e_val)>0)
    model.mets(real(e_val)>0)
%     fprintf('%d %3.6g %d\n',find(real(e_val)>0));
end
% Nimc_obj = deriv(Nimc,eye(model.nt_metab));
% dXdtADMAT = ODEmodelADMAT(0,Nimc_obj,[],model,pvec);
% Y = getval(dXdtADMAT);
% Jac = getydot(dXdtADMAT);

%integrate model
[sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
% [model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,10.0);

%integrate model
% [sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
% [model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,1e3);

%integrate model
% [sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
% [model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,5e3);

%integrate model
% [sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
[model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,1e4);

%integrate model
[sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
% [model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,5e4);

%integrate model
% [sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
[model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,9e4);

%integrate model
[sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
[model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,5e5);

%integrate model
[sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
[model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,1e6);

%integrate model
[sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
[model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,5e6);

%integrate model
[sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);

%initialize solver properties
[model,solverP,saveData] = imodel(model,ess_rxn,Vup_struct,1e7);

%integrate model
[sol,finalSS,status] = callODEsolver(model,pvec,Nimc,solverP);




