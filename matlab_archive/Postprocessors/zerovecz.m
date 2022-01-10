function zeroVec = zerovecz (vecAvsIn)

%Read in _vec_node.avs file, zeroing z components.
%SYNTAX
%   zerovecz(outfile) outputs x,y,0 values to output file with the same
%   root name and a '_zeroed_vec_node.avs' extension.
%
%EXAMPLE
%   zeroVec = zerovecz('vectest_vec_node.avs');
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2015/04/08

if nargin<1
    disp('Locating _vec_node.avs file...')
    vecAvsIn = getfile('*_vec_node.avs');
end

outFile = [vecAvsIn(1:end-13),'_zeroed_vec_node.avs'];

disp(['Reading file: ', vecAvsIn])
zeroVec = getavs(vecAvsIn);

%Zero z values
zeroVec(:,3)=0;


%Write to avs file
vec2avs(zeroVec,outFile);


end