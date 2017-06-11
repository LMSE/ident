% optimization of flux parameters in kotte model for a CK formulation
function [x_opt,opt_id,new_opt_p,fval] =...
        flux1_k_noisy(opts,xss,fss,plist,init_xss)
if nargin<5
    init_xss = [];
end    
if isfield(opts,'opt_x0')
    x0 = opts.opt_x0;
end

% flux 1    
p_id = cellfun(@(x)strcmpi(plist,x),{'K1ac','k1cat'},'UniformOutput',false);
p_id = cellfun(@(x)find(x),p_id);
% p = opts.odep(p_id)';
% p = [.1;.1];


% x0 = [init_xss;...      
%       p;...
%       0.01]; % x = [pep;fdp;enz;K1ac;k1cat;e];
% steady state experimental concetrations and fluxes needed for constraints
% fed as parameters
% ac = opts.odep(17);
% nopt_p = opts.odep(setdiff(1:length(opts.odep),p_id));
% optim_p = nopt_p';
optim_p = opts.odep;
opts.p_id = p_id;
ss_val = [xss(:,1:4);...
          fss(:,1:4)];

% all concentrations as well as kientic parameters are variables
% lb = [pep;fdp;e;ac] - acetate is a equality constraint (fixed parameter)
lb = [0;0;0;1e-3;1e-3;0]; 
ub = [20;20;20;10;10;20];
% [x_opt,fval,~,~,opts] =...
% nlconstoptim_flux(opts,@obj_flux1_noisy_CAS,lb,ub,x0,...
%                   optim_p,ss_val,0,@constr_flux1_noisy_CAS); % linear objective
[x_opt,fval,~,~,opts] =...
nlconstoptim_flux_noCAS(opts,@obj_flux1_noisy,lb,ub,x0,...
                  optim_p,ss_val,0,@constr_flux1_noisy); % linear objective              

% check flux using conkin rate law
if ~isempty(init_xss)
    opts.odep = init_xss;
% else
%     pconv = [.1;.3;0]; % extra parameters for CK 'K1pep','K2fdp','rhoA'
%     opts.odep = [opts.odep';pconv];
end
opt_id = p_id; % [p_id,14];
opts.odep(opt_id) = x_opt(4:end-1);
new_opt_p = opts.odep;
