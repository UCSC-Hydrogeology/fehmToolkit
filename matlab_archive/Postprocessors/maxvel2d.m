function maxvel = findmaxv (vecAvsIn)
%Read in _vec_node.avs file, find maximum in third column (velocity)
%EXAMPLE
%   maxvel = findmaxv('vectest_vec_node.avs');
%
%   Written by Tess Weathers, UCSC Hydrogeology
%   Revision: 1.0 , 2018/04/16
%
%   
%

if nargin<1
    disp('Locaticng _vec_node.avs file...')
    vecAvsIn = getfile('*_vec_node.avs');
end

disp(['Reading file: ', vecAvsIn])
avsMatrix = getavs(vecAvsIn);

%Find max values
if sum(avsMatrix(:,3))>0
    maxvelocity = max(avsMatrix(:,3));
    maxvelocity
end
if sum(avsMatrix(:,3))==0
    maxvelocity = max(avsMatrix(:,2));
    maxvelocity
end


end