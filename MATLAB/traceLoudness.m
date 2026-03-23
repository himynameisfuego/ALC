function [filtTrace,f] = traceLoudness(ML,LL);

% [filtTrace,f] = traceLoudness(ML,LL);
%
% Returns filtering trace-guide from ELLC (Equal-loudness level contours).
% 
% OUTPUTS:
% filtTrace: trace-guide, set of curves of ideal compensation
% f: frequency vector
%
% INPUTS:
% ML: Mastering Level; LL = Listening Level  
%
% Fierro Leonardo 05.10.2018
% Modified 10.10.2018

%% Calculate SPLs
phon = 20:10:90;
[spl,f] = ellc(phon');

%% Fitting
phonFit = 20:1:90;
Npoints = size(spl,2);
spl_fit = zeros(length(phonFit),Npoints);

for i = 1:Npoints
    v = spl(:,i)';
    vq = interp1(phon,v,phonFit);
    spl_fit(:,i) = vq';
end

%% Difference from mastering
if nargin < 2
    LL = 30;
end

MdB = find(phonFit == ML);
masterCurve = spl_fit(MdB,:);
LdB = find(phonFit == LL);
listenCurve = spl_fit(LdB,:);

diffCurve = masterCurve - listenCurve - ML + LL;
filtTrace = -diffCurve;
