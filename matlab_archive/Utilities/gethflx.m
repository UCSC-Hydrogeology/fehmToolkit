function [hflxOut, hflxNode] = gethflx(hflxFile)

%Reads heat flux values from .hflx file, returning values as a vector.
%SYNTAX
%   hflxOut = gethflx(hflxFile) reads data from .hflx file,
%   returning an Nx1 vector, where N is the number of nodes in the
%   top grid surface.
%
%   [hflxOut, hflxNode] = gethflx(hflxFile) also returns node numbers for
%   all heat flux values returned.
%
%EXAMPLE
%   hflx = gethflx('grid_2.hflx');
%
%   See also GETFIN, GETAVS, GETPROP.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2015/07/22

if nargin < 1
    hflxFile = getfile('*.hflx');
end

disp(['Reading file: ',hflxFile])

fid=fopen(hflxFile);
hflxIn = cell2mat(textscan(fid, '%f %f %*f %f %*f', 'HeaderLines', 1));
fclose(fid);

%Drop the trailing zero
hflxIn = hflxIn(1 : end - 1, :);

%Convert short format from file into long form, with one row per node
node1 = hflxIn(:, 1);
node2 = hflxIn(:, 2);
hflxIn = hflxIn(:, 3);

hflxNode = [];
hflxOut = [];
for i = 1:length(hflxIn)
    hflxNode = [hflxNode; (node1(i) : node2(i))'];
    hflxOut = [hflxOut; repmat(hflxIn(i), 1 + node2(i) - node1(i), 1)];
end

end