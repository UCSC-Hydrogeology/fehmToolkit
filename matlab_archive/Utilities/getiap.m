function Piap=getiap(iapfile_in)

%Read pressure data from .iap or .icp file.
%SYNTAX
%   P = getiap(iapfile_in) reads pressure from .iap file
%
%EXAMPLE
%   P = getiap('grid_3_restart.iap');
%
%   See also GETFIN, FIN2INI.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2015/07/30

if nargin<1
    fprintf('%s\n\n','Locating IPRES output (.iap) file...')
    iapfile_in=getfile('*.iap');
end

fprintf('%s\n\n','Locating FEHM (.fehm) file...')
fehmfile=getfile('*.fehm*');

disp(['Reading # of nodes from: ',fehmfile])
fid=fopen(fehmfile);
fgetl(fid);
n=cell2mat(textscan(fid,'%u',1));
fclose(fid);

%Read iap file
disp(['Reading file: ',iapfile_in])
fid=fopen(iapfile_in);
[~]=cell2mat(textscan(fid,'%f',n));
Piap=cell2mat(textscan(fid,'%f',n));
fclose(fid);

end