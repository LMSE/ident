function [x,assignFlag,delGr,vCorrectFlag] = getiConEstimate(model)

%setup problem with default constraints for thermodynamically active
%reaction
% delG > or < 0 and Vss < or > 0
bounds = setupMetLP(model);

%check
if ~isfield(bounds,'A') 
    error('getiest:NoA','No stoichiometric transpose found');
end
if size(bounds.A,2) == length(bounds.mets)
    
    %setup slack problem
    bounds = setupSlackVariables(bounds);
    
    %solve once more to  obtain consistent concentrations  size(bounds.A,2)  
    LPmax = solvemetLP(bounds);
    if LPmax.flag>0 
        %do not include slack variables
        x = separate_slack(LPmax.x,model,bounds);
%         check_1(bounds,x);
        %get mc for model and check for delGr values
        if ~isempty(x)
            [x,assignFlag,delGr,vCorrectFlag] = assignConc(x,model,bounds);        
        end
        if ~isempty(delGr)
            [delGr,assignFlux] = assignRxns(delGr,model,bounds);
        end
        
        mc = exp(x);
        mc(x==0)=0;
        x = mc;
    else
        error('mcEst:LPinfeas',...
            'LP for thermodynamic metabolite conentrations is infeasible');
    end
else
    error('getiConEst:sizeCheck',...
        'Number of metabolites in bounds.S and bounds.mets do not match');
end

%concentrations for thermodynamically inactive reactions
%delG = 0 and Vss = 0

function delGr = checkdelGr(model,mc)

%eliminate consideration for excess cofators
%pi[c],pi[e],h[c],h[e],h2o[c]
pic = find(strcmpi(model.mets,'pi[c]'));
pie = find(strcmpi(model.mets,'pi[e]'));
hc = find(strcmpi(model.mets,'h[c]'));
he = find(strcmpi(model.mets,'h[e]'));
h2o = find(strcmpi(model.mets,'h2o[c]'));

vspl = [find(strcmpi(model.rxns,'THD2'))...
        find(strcmpi(model.rxns,'NADH16'))...
        find(strcmpi(model.rxns,'ATPS4r'))];

%check for delGr values
Vind = model.Vind;
delGr = zeros(model.nt_rxn,1);
for irxn = 1:length(model.Vind)
    if ismember(Vind(irxn),vspl)
        q8 = find(strcmpi(model.mets,'q8[c]'));
        q8h2 = find(strcmpi(model.mets,'q8h2[c]'));
    else
        q8 = [];
        q8h2 = [];
    end
    sbid = model.S(:,Vind(irxn))<0;
    prid = model.S(:,Vind(irxn))>0;
    sbid([pic pie hc he h2o q8 q8h2]) = 0;
    prid([pic pie hc he h2o q8 q8h2]) = 0;
    sb = prod(mc(sbid));
    pr = prod(mc(prid));
    delGr(Vind(irxn)) = 0.008314*298*log(pr/(sb*model.Keq(Vind(irxn))));
%     fprintf('delG = %2.3g \t Vss = %3.4g \n',delGr(Vind(irxn)),model.Vss(Vind(irxn)));
    
end