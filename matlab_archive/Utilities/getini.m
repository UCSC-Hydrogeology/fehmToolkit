function [tsp,header]=getini(inifile_in)

%Read temperature, saturation, and pressure data from .ini file.
%SYNTAX
%   tsp = getini(inifile_in) reads temperature, saturation, and pressure
%   from .ini file 'inifile_in'. Returns an Nx3 matrix [T,S,P], where N is
%   the number of nodes in the grid, and the row number corresponds to the
%   node number.
%
%   [tsp, header] = getini(inifile_in) also reads the header as a 5x1 cell
%   array.
%
%EXAMPLE
%   tsp = getini('grid_3_restart.ini');
%
%   See also GETFIN, GETPT, FIN2INI.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/18

if nargin<1
    fprintf('%s\n\n','Locating FEHM output (.ini) file...')
    inifile_in=getfile('*.ini');
end

%Read fin file
disp(['Reading file: ',inifile_in])
fid=fopen(inifile_in);
header=cell(4,1);
for i=1:4, header{i}=fgetl(fid);end
n=cell2mat(textscan(header{4},'%f%*s'));
T=cell2mat(textscan(fid,'%f',n,'Headerlines',1));
S=cell2mat(textscan(fid,'%f',n,'Headerlines',2));
P=cell2mat(textscan(fid,'%f',n,'Headerlines',2));
fclose(fid);

tsp=[T,S,P];

end