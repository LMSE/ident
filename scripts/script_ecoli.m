%script_ecoli
clc

addpath(genpath('C:\Users\shyam\Documents\Courses\CHE1125Project\IntegratedModels\KineticModel'));
rxfname = 'C:\Users\shyam\Documents\Courses\CHE1125Project\IntegratedModels\KineticModel\ecoliN1.txt';

%create model structure
[FBAmodel,parameter,variable,nrxn,nmetab] = modelgen(rxfname);

%% %CRNT analysis of model - require ERNEST TB for MATLAB
% [SBMLmodel,result] = CRNTanalysis(FBAmodel);

%add rxn
% rxn.equation = 'atp[c] <==>';
% FBAmodel = addRxn(FBAmodel,parameter,rxn);

%% FBA or pFBA solution - optional
%fix flux uptakes for FBA solution
Vup_struct.exGLC = 20;%mmol/gDCW.h
Vup_struct.exO2 = 1000;%mmole/gDCW.h

%designate reactions for which uptake should not be zero in FBA
ess_rxn = {'exCO2','exH','exH2O','exPI','exO2','exGLC'};

%Optional - FBAmodel.Vss already has the requiste information from the
%excel file
%assign initial fluxes and calculate FBA fluxes for direction
FBAmodel = FBAfluxes(FBAmodel,'fba',ess_rxn,Vup_struct);

%% Metabolite conecntrations 
%extracellular metabolites in M moles/L
% met.glc_e = 0.2;
% met.h_e = 1e-7;
% met.h_c = 1e-7;
met.h2o_c = 55.0;%1.53e-13;
met.h2o_e = 55.0;%55.0;
met.o2_e = 0.0025;
met.pi_e = 4e-2;
% met.pi_c = 1e-3;
met.co2_e = 0.002;%1e-8;

%obtain conentrations from file
%fname = '';
% mc = readCNCfromFile(fname,model);

%or

%samwple initial metabolite concentrations for estimating kinetic parameters
[mc,parameter,smp] = parallel_sampling(FBAmodel,parameter,met,'setupMetLP',500);

%get one set of concentrations and coresponding delGr
% [x,delGr,assignFlag,vCorrectFlag] = getiConEstimate(FBAmodel);

%get more than one set of concentrations using ACHR sampling
% ACHRmetSampling(FBAmodel,1,500,200)

%% Build model parameters as an ensemble
%Reactions to be considered cytosolic even if defined otherwise
%reactions to consider for kinetics other than Vind
rxn_add = {'GLCpts','NADH16','ATPS4r','NADTRHD','THD2','CYTBD'};

%reactions not be considered cytosolic even if defined otherwise
rxn_excep = {'ATPM'};

FBAmodel.rxn_add = rxn_add;
FBAmodel.rxn_excep = rxn_excep;

%get parameter estimates - estimate kinetic parameters in an ensemble
ensb = parallel_ensemble(FBAmodel,mc,parameter,rxn_add,rxn_excep);

%load a pre determined model
% load('C:\Users\Shyam\Documents\Courses\CHE1125Project\mat_files\KineticModel\ecoliN1_newpvec_1.mat');
% load('C:\Users\Shyam\Documents\Courses\CHE1125Project\mat_files\KineticModel\ecoliN1_pvec2_Jan17.mat');
% load('C:\Users\Shyam\Documents\Courses\CHE1125Project\mat_files\KineticModel\ecoliN1_pvec_Jan18.mat');

% x = initialsample(FBAmodel);

%% Integrate kinetic model of metabolic network
%change initial conditions to simulate a perturbation
change_pos(1).glc_e = 1;
change_pos(2).glc_e = 10;
% change_pos = [];

if size(ensb,1)>1 
    %run a parallel version to solve all odes
    sol = IntegrateModelEnsemble(FBAmodel,ess_rxn,Vup_struct,ensb,ensb{1,1},change_pos);
else
    %serially solve ODE of model to steady state
    if ensb{1,2}.feasible    
        sol = IntegrateModel(FBAmodel,ensb,ensb{1,1},ess_rxn,Vup_struct,change_pos);
    else
        error('No feasible model found');
    end
end

%Perturbation to concentrations
[sol] = MonteCarloPertrubationIV(model,ess_rxn,Vup_struct,ensb,initval,VMCpos,VMCneg,np);