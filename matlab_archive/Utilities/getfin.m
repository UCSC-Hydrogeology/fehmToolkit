function [tsp,header]=getfin(finfile_in)

%Read temperature, saturation, and pressure data from .fin file.
%SYNTAX
%   tsp = getini(finfile_in) reads temperature, saturation, and pressure
%   from .fin file 'inifile_in'. Returns an Nx3 matrix [T,S,P], where N is
%   the number of nodes in the grid, and the row number corresponds to the
%   node number.
%
%   [tsp, header] = getini(finfile_in) also reads the header as a 5x1 cell
%   array.
%
%EXAMPLE
%   tsp = getini('grid_3.fin');
%
%   See also GETINI, GETPT, FIN2INI.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/18

if nargin<1
    fprintf('%s\n\n','Locating FEHM output (.fin) file...')
    finfile_in=getfile('*.fin');
end

[tsp,header]=getini(finfile_in);

end