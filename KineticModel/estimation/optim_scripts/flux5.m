% optimization of flux parameters in kotte model for a CK formulation
function [x_opt,opt_pid,new_opt_p,fval] =...
        flux5(opts,xss2,fss2,plist,old_opt_p)
if nargin<5
    old_opt_p = [];
end
    
% flux 3 
p_id = cellfun(@(x)strcmpi(plist,x),{'vemax','KeFDP','ne'},'UniformOutput',false);
p_id = cellfun(@(x)find(x),p_id);
p = opts.odep(p_id)';

f3 = fss2(2); % add steayd state experimental flux
optim_p = [xss2;f3]; % concentrations & fluxes (expt) are parameters
lb = [1e-3;1e-6;1];
ub = [2000;20;4];
[x_opt,fval,~,~,opts] = runoptim_flux(opts,@obj_flux5_CAS,lb,ub,p,optim_p);

% check flux using conkin rate law
if ~isempty(old_opt_p)
    opts.odep = old_opt_p;
% else
%     pconv = [.1;.3;0]; % extra parameters for CK 'K1pep','K2fdp','rhoA'
%     opts.odep = [opts.odep';pconv];
end
opt_pid = p_id; % [p_id,16];
opts.odep(opt_pid) = x_opt;
new_opt_p = opts.odep;