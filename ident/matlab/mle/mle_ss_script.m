% get maximum likelihood estimate of all parameters for given experimental
% data (noisy)
%% load noisy data
if ~exist('C:\Users\shyam\Documents\Courses\CHE1125Project\IntegratedModels\KineticModel')
    status = 2;
    fprintf('\nLinux System\n');
else 
    status = 1;
    fprintf('\nWindows System\n');
end

if status == 1    
    load('C:/Users/shyam/Documents/Courses/CHE1125Project/IntegratedModels/KineticModel/estimation/noisy_model/pdata_oct2');
elseif status == 2    
    load('~/Documents/Courses/CHE1125Project/IntegratedModels/KineticModel/estimation/noisy_model/pdata_oct2');    
end

%% collect only needed perturbations for analysis
avail_pert = size(noisy_sol{1},2);
use_pert = 1:8;
npert = length(use_pert);
[exp_select_sol,noisy_select_sol] = parseperturbations(noisy_sol{1},use_pert);

% use wt as initial value for all perturbations
xinit = noisy_xss(:,1);
yinit = noisy_fss(:,1);
input_data = exp_select_sol.exp_pval;

freq = .1;
% pd = makedist('Normal','mu',0,'sigma',.05);
% ynoise = random(pd,4,length(freq));
% ynoise = exp_select_sol.noise_fdyn([1 3 4 5],freq);
ynoise_var = .01;
logL_const = -length(freq)/2*sum(log(ynoise_var));

mle_opts = struct('nc',3,'nf',6,'npert',npert,...                  
                  'casmodelfun',@kotteCASident,...
                  'xinit',xinit,...
                  'yinit',yinit,...
                  'xexp',exp_select_sol.xss([1 2],:),...
                  'yexp',exp_select_sol.fss([1 3 4 5],:),...
                  'ynoise_var',ynoise_var,...
                  'input_data',input_data,...
                  'wcon',1,...
                  'odep',odep_bkp,...
                  'tspan',opts.tspan,...
                  'freq',freq,...                  
                  'logL_const',logL_const);

%% get MLE of all parameters
% initial value for optimization
scale = ones(9,1);
scale(3) = 1e6;
p0 = [odep_bkp(1:5)';odep_bkp(10:13)']./scale;

% MLEvals = getMLE(mle_opts,p0,scale);  
MLE_noisy = getmle_ss(mle_opts,p0,scale);