function [nod,header] = getnod (nodfile_in)

%Read tracer information from .trc file.
%SYNTAX
%   nod = getnod(nodfile_in) reads data from .nod file,
%   generated from python script separate_files_by_node.py
%   returning an NxM matrix, where N is the number of timesteps in the
%   simulation, and M is the number of data columns present.
%
%   [nod, header] = getnod(nodfile_in) also returns the header of the nod
%   file as a string.
%
%EXAMPLE
%   nodes = getnod('run_244354.nod');
%
%   See also GETFIN, GETHFLX, GETPROP.
%
%   Written by Tess Weathers, UCSC Hydrogeology
%   Revision: 1.0 2018/07/17
%       Modified getavs to getnod

if nargin<1
    disp('Locating .nod file...')
    nodfile_in=getfile('*.nod');
end

%Read nod
fprintf('%s\t%s\n','Reading file: ',nodfile_in)
fid=fopen(nodfile_in);
nod=cell2mat(textscan(fid,'%f%f','headerLines',2,'delimiter',','));
fclose(fid);

end