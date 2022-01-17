function [vol,header] = getstor (storfile_in)

%Read volume data from .stor file.
%SYNTAX
%   vol = getstor(storfile_in) reads volume data from .stor file,
%   returning an Nx1 vector, where N is the number of nodes in the
%   grid.
%
%EXAMPLE
%   V = getstor('grid_2.stor');
%
%   See also GETFIN, GETINI, GETPROP, GETAVS.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/08/23

if nargin<1
    disp('Locating .stor file...')
    storfile_in=getfile('*.stor');
end

%Read .stor
fprintf('%s\t%s\n','Reading file: ',storfile_in)
fid=fopen(storfile_in);
header=textscan(fid,'%s',3,'Delimiter','\n');
header=header{1};
n=cell2mat(textscan(header{3},'%*f %f %*f %*f %*f'));
vol=cell2mat(textscan(fid,'%f',n));
fclose(fid);

end