function [s,mssid,nss] = setupMATCONT(allxeq,allpvec,ap,model,fluxg,npts)

for ipt = 1:npts
    fprintf('\nIteration #%d of %d Equilibrium Continuation...\n',ipt,npts);
    
    xeq = allxeq(:,ipt);
    pvec = allpvec(ipt,:);
    
    % change to bigger number if bifurcation starts at a bigger value
    pvec(ap) = 0.01;
    
    % run MATCONT
    [data,y,p] = execMATCONT(xeq,pvec,ap,fluxg,model);
    if ~isempty(data) && size(data.s1,1)>2
%         bifurcationPlot(data.flux,data.s1,data.f1,[5,3]);
        hbif1 = bifurcationPlot(data.x1,data.s1,data.f1,[4,1],ap);    
%         bifurcationPlot(data.x1,data.s1,data.f1,[4,2]);
%         bifurcationPlot([data.flux;data.x1(end,:)],data.s1,data.f1,[6,5]);
    end
    
    % save MATCONT results
    s.(['pt' num2str(ipt)]) = data;
    
    % get the mss for y and p
    if ~isempty(data)
        [yss,iyval,fyval] = parseMATCONTresult(data.s1,y);
        [pss,ipval,fpval] = parseMATCONTresult(data.s1,p);
        [fss,ifval,ffval] = parseMATCONTresult(data.s1,data.flux);
    end
        
    fprintf('Equilibrium Continuation Complete\n');
    clear pvec xeq data y p
end

% check which solutions have mss
mssid = [];
nss = zeros(npts,1);
for ipt = 1:npts
    if ~isempty(s.(['pt' num2str(ipt)]))
        s1 = s.(['pt' num2str(ipt)]).s1;
        nLP = size(s1,1);
        if nLP > 2
            fprintf('Vector %d has %d Steady States\n',ipt,nLP);
            mssid = union(mssid,ipt);
            nss(ipt) = nLP;
        end
    else
        fprintf('No convergence at %d\n',ipt);
    end
end