function iap2ini (inifile_out,sourcedir)

%Rewrites .iap file as .ini, using temperatures from .fin file and zeroing
%the time header.
%SYNTAX
%   iap2ini() rewrites a local '.iap' file FILENAME.iap as FILENAME.ini,
%   changing format appropriately. Uses a local '.fin' file for temperature
%   data and header. The initial time (third line of the header) is reset
%   to zero.
%
%   iap2ini(inifile_out) rewrites a local '.iap' file as 'inifile_out',
%   changing format appropriately. Uses a local '.fin' file for temperature
%   data and header. The initial time (third line of the header) is reset
%   to zero.
%
%   iap2ini(inifile_out,sourcedir) instead looks in 'sourcedir' for the
%   source '.iap' and '.fin' file.
%
%EXAMPLE
%   iap2ini()
%
%   iap2ini('NewRun.ini')
%
%   iap2ini('new_models/run1/run1.ini','old_models/run12')
%
%   See also FIN2INI, MKFEHMDIR, APPENDZONE.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2014/01/13

%INPUT
%--------------------------
if nargin<2, sourcedir='.';end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

fprintf('%s\n','Locating FEHM output (.fin) file...')
finfile=getfile([sourcedir,'*.fin']);

fprintf('%s\n\n','Locating ipres output (.iap) file...')
iapfile=getfile([sourcedir,'*.iap']);

root=iapfile(1:end-4);

if nargin<1, inifile=[root,'.ini'];
else inifile=inifile_out;
end

%Read iap
disp(['Reading file: ',iapfile])
fid=fopen(iapfile);
iap_in=cell2mat(textscan(fid,'%f'));
fclose(fid);

%Read fin header
disp(['Reading file: ',finfile])
fid=fopen(finfile);
header=cell(4,1);
for i=1:4, header{i}=fgetl(fid);end
fclose(fid);
header{3}='   0000000000.000000';

%Read T from finfile
fid=fopen(finfile);
T=textscan(fid,'%f','Headerlines',5);
fclose(fid);
T=T{:};

%Parse inputs
n=cell2mat(textscan(header{4},'%f%*s'));
S=iap_in(1:n);
P=iap_in(n+1:end);

if ~isequal(length(S),n) || ~isequal(length(P),n)
    warning('iap2ini:InconsistentNodes',...
        ['Number of nodes present in .iap (or .icp) inconsistent',...
        'with number of nodes in .fin file. Recheck files.'])
end

clearvars iap_in

%OUTPUT
%--------------------------
disp(['Writing file: ',inifile])

fid=fopen(inifile,'w');
fprintf(fid,'%s\n',header{:});
fprintf(fid,'%s','temperature');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',T);
fprintf(fid,'\n%s','saturation');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',S);
fprintf(fid,'\n%s','pressure');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',P);
fprintf(fid,'\n%s','no fluxes');
fclose(fid);

end