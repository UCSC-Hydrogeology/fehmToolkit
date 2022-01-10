function maxconc = findmaxc (nodIn)
%Read in _vec_node.avs file, find maximum in third column (velocity)
%EXAMPLE
%   maxvel = findmaxv('vectest_vec_node.avs');
%
%   Written by Tess Weathers, UCSC Hydrogeology
%   Revision: 1.0 , 2018/04/16

if nargin<1
    disp('Locating .nod file...')
    nodIn = getfile('*nod');
end

disp(['Reading file: ', nodIn])
nodMatrix = getnod(nodIn);

%Find max values

maxconcentration = max(nodMatrix(:,2));
maxconcentration;

i=find(nodMatrix(:,2)==maxconcentration);
maxtime=nodMatrix(i,1)-4746

%Create array for the front of breakthrough
front=nodMatrix(1:i,:);

%Find nearest time to 50% max concentration in front
exacthalfmax=0.5*maxconcentration;
[d,ix]=(min(abs(front(:,2)-exacthalfmax)));

halfmax=front(ix,2);
halftime=front(ix,1)-4746;

%Display results
fprintf('Node number %s\n',nodMatrix(1:1))
fprintf('%s: Max conc. (mol/L)\n',maxconcentration)
fprintf('%f: Time of max conc. (days post injection)\n',maxtime)
fprintf('%s: Approx. half conc. (mol/L)\n',halfmax)
fprintf('%s: Time to half conc. (days post injection)\n',halftime)
fprintf('%s\t%f\t%s\t%s\n',maxconcentration,maxtime,halfmax,halftime)


end