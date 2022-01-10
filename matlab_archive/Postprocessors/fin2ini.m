function fin2ini (inifile_out,sourcedir,useiap_outsidezone)

%Rewrites .fin file as .ini, zeroing the time header.
%SYNTAX
%   fin2ini() rewrites a local '.fin' file FILENAME.fin as FILENAME.ini.
%   The initial time (third line of the header) is reset to zero.
%
%   fin2ini(inifile_out) rewrites a local '.fin' file as 'inifile_out'. The
%   initial time (third line of the header) is reset to zero.
%
%   fin2ini(inifile_out,sourcedir) instead looks in 'sourcedir' for the
%   source '.fin' file.
%
%   fin2ini(inifile_out,sourcedir,useiap_outsidezone) also resets pressure
%   values on the boundary specified by 'useiap_outsidezone' to those found
%   in an '.iap' file in 'sourcedir'. 'useiap_outsidezone' is either a
%   numeric zone number, or a string containing a title appearing before a
%   zone (e.g. 'top', or 'left_w') in an '_outside.zone' file within
%   'sourcedir'.
%       This functionality should be used when setting up a restart run, as
%       pressure values on the boundary (used to set BCs for the next run)
%       may drift slightly from initial conditions during the run.
%
%EXAMPLE
%   fin2ini()
%
%   fin2ini('NewRun.ini')
%
%   fin2ini('new_models/run1/run1.ini','old_models/run12','top')
%
%   See also GETZONE, MKFEHMDIR, IAP2INI, APPENDZONE.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2014/01/13

%INPUT
%--------------------------
if nargin<3,useiap_outsidezone=0;end
if nargin<2,sourcedir='.';end

if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

fprintf('%s\n','Locating FEHM output (.fin) file...')
finfile=getfile([sourcedir,'*.fin']);

root=finfile(1:end-4);

if nargin<1, inifile_out=[root,'.ini'];end

if useiap_outsidezone
    fprintf('%s\n','Locating AMBIENT HYDROSTAT (.iap) file...')
    iapfile=getfile([sourcedir,'*.iap']);
    
    fprintf('%s\n','Locating OUTSIDE ZONE (_outside.zone) file...')
    outsidefile=getfile([sourcedir,'*_outside.zone']);
end

%Read fin file
[TSP,header]=getfin(finfile);

header{3}='   0000000000.000000';
n=cell2mat(textscan(header{4},'%f%*s'));

if useiap_outsidezone
    %Read _outside.zone file
    fprintf('%s\n',['Reading file: ',outsidefile])
    nodes=getzone(useiap_outsidezone,outsidefile);
    
    %Read iap file
    disp(['Reading file: ',iapfile])
    fid=fopen(iapfile);
    [~]=cell2mat(textscan(fid,'%f',n));
    Piap=cell2mat(textscan(fid,'%f',n));
    fclose(fid);
    
    %Replace specified values
    TSP(nodes,3)=Piap(nodes);
end

%OUTPUT
%--------------------------

disp(['Writing output to file: ',inifile_out])
fid=fopen(inifile_out,'w');
fprintf(fid,'%s\n',header{:});
fprintf(fid,'%s','temperature');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',TSP(:,1));
fprintf(fid,'\n%s','saturation');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',TSP(:,2));
fprintf(fid,'\n%s','pressure');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',TSP(:,3));
fprintf(fid,'\n%s','no fluxes');
fclose(fid);

end