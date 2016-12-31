% generate equilibrium solution and model for Kotte model
if ~exist('C:\Users\shyam\Documents\Courses\CHE1125Project\IntegratedModels\KineticModel\Kotte2014\Kotte2014.txt')
    status = 2;
    fprintf('\nLinux System\n');
else 
    status = 1;
    fprintf('\nWindows System\n');
end
if status == 1
    rxfname = 'C:\Users\shyam\Documents\Courses\CHE1125Project\IntegratedModels\KineticModel\Kotte2014\Kotte2014.txt';
    cnfname = 'C:\Users\shyam\Documents\Courses\CHE1125Project\IntegratedModels\KineticModel\Kotte2014\Kotte2014C.txt';
elseif status == 2
    rxfname = '/home/shyam/Documents/MATLAB/Code/KineticModel/Kotte2014/Kotte2014.txt';
    cnfname = '/home/shyam/Documents/MATLAB/Code/KineticModel/Kotte2014/Kotte2014C.txt';
end

% create model structure
[FBAmodel,parameter,variable,nrxn,nmetab] = modelgen(rxfname);

% obtain conentrations from file
[mc,FBAmodel,met] = readCNCfromFile(cnfname,FBAmodel);

% run FBA
Vup_struct.ACt2r = 1;
Vup_struct.ENZ1ex = 1;
FBAmodel = FBAfluxes(FBAmodel,'fba',{'ACt2r','ENZ1ex'},Vup_struct,...
                    [find(strcmpi(FBAmodel.rxns,'FDex'))...
                     find(strcmpi(FBAmodel.rxns,'PEPex'))]);
                 
% remove metabolites held constant from consideration in the model
% integration phase
[model,pvec,newmc,cnstmet] =...
remove_eMets(FBAmodel,parameter,mc,[FBAmodel.Vind FBAmodel.Vex],...
{'enz1[c]','enz1[e]','enz[e]','ac[e]','bm[c]','bm[e]','pep[e]'});    

% only initialize for varmets   
nvar = length(model.mets)-length(find(cnstmet));
M = newmc(1:nvar);
PM = newmc(nvar+1:end);
model.PM = PM;

% call to parameter sampling script for analysis of mss
% parameters
clear pvec
kEcat = 1;
KEacetate = 0.1;    % or 0.02
KFbpFBP = 0.1;
vFbpmax = 1;
Lfbp = 4e6;
KFbpPEP = 0.1;
vEXmax = 1;
KEXPEP = 0.3;
vemax = 1.1;        % for bifurcation analysis: 0.7:0.1:1.3
KeFBP = 0.45;       % or 0.45
ne = 2;             % or 2
acetate = 0.1;      % a.u acetate
d = 0.25;           % or 0.25 or 0.35
kPEPout = 0.2;
pvec = [KEacetate,KFbpFBP,Lfbp,KFbpPEP,...
        KEXPEP,vemax,KeFBP,ne,acetate,d,...
        kPEPout,kEcat,vFbpmax,vEXmax];
    
% systems check
givenModel = @(t,x)KotteODE(t,x,model,pvec);
givenMfsolve = @(x)Kotte_givenNLAE(x,model,pvec);
fluxg = Kotte_givenFlux([M;model.PM],pvec,model);
dMdtg = givenModel(0,M);

tspan = 0:0.1:500;    
npts = 1;
allpvec = pvec;  

% run equilibrium solution followed by MATCONT
opts = odeset('RelTol',1e-12,'AbsTol',1e-10);
ac = find(strcmpi(model.mets,'ac[e]'));
allxeq = zeros(length(M),npts);
allxdyn = zeros(length(M),length(tspan),npts);
allxf = zeros(length(M),npts);
allfeq = zeros(length(fluxg),npts);
allfdyn = zeros(length(fluxg),length(tspan),npts);
ap = 9;
solveEquilibriumODE    

% get saddle node
[saddle,saddlepar] = getsaddlenode(data.s1,data.x1,5e-3);
% get all parameter (saddles) values between the 2 limit points
allsaddles = extractsaddles(data.s1,data.x1);
nsadpts = size(allsaddles,2);

% get eigval and eig vec for all saddle points
alleig = zeros(nvar,nsadpts);
allw = zeros(nvar,nvar,nsadpts);
tspanr = 0:-.1:-30;
tspanf = 0:0.1:2000;
eps = 1e-4;
allWus = zeros(nvar,length(tspanr),nsadpts);

for ipts = 1:nsadpts
    pvec(ap) = allsaddles(end,ipts);
    model.PM(ac-length(saddle)) = allsaddles(end,ipts);
    
    % get eig val and eig vector
    [~,alleig(:,ipts),w] = getKotteJacobian(allsaddles(1:3,ipts),pvec,model);
    allw(:,:,ipts) = w;
    
    % calculate unstable manifold for all saddle points
    [xWus,xeq] = calc1DWus(allsaddles(1:3,ipts),w,alleig(:,ipts),model,pvec,opts,tspanr,tspanf,eps);
    
    % collect reverse trajectory 
    allWus(:,:,ipts) = xWus;
end

%% unstable manifold in 3D
% figure
allx = [];ally = [];allz = [];
for jpt = 1:nsadpts    
    [~,nzid,~] = find(allWus(:,:,jpt)~=0,1,'last');
    relWus = allWus(:,1:nzid,jpt);
    kid = relWus(1,:)<0|relWus(1,:)>5|relWus(2,:)<0|relWus(2,:)>5|relWus(3,:)<0|relWus(3,:)>5;
    relWus(:,kid) = [];
    allx = [allx relWus(1,:)];
    ally = [ally relWus(2,:)];
    allz = [allz relWus(3,:)];
%     hold on
%     plot3(relWus(1,:),relWus(2,:),relWus(3,:),'LineStyle','none','Marker','.','Color','r');    
end
hfig = Manifold2DPlot(allx,ally,allz);


% perturbManifolds(xmafold(1:3,:)',saddle,model,pvec,opts,tspanf,...
%                         hfig,[1 2 3],10); 