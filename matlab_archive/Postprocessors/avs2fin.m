function avs2fin(finfile_out,sourcedir,avsfile)

%Rewrites .fin or .ini file with info from .avs file and .ini, resetting the time
%header.
%   SYNTAX avs2fin() rewrites a local '.avs' file FILENAME.avs as
%   FILENAME.fin, or FILENAME.ini. The initial time (third line of the
%   header) is reset to zero.
%
%   avs2fin(finfile_out) rewrites a local '.avs' file as 'finfile_out'. The
%   initial time (third line of the header) is reset to zero.
%
%   avs2fin(finfile_out,sourcedir) instead looks in 'sourcedir' for the
%   source files.
%
%   avs2fin(finfile_out,sourcedir,avsfile) specifies the avs input file to
%   be used.
%
%EXAMPLE
%   avs2fin()
%
%   avs2fin('NewRun.fin','olddir/','test.avs')
%
%   See also AVS2INI, GETZONE, MKFEHMDIR, IAP2INI, APPENDZONE.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2014/01/13

%INPUT
%--------------------------
if nargin<2,sourcedir='.';end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

if nargin<3
fprintf('%s\n','Locating scalar node (_sca_node.avs) file...')
avsfile=getfile([sourcedir,'*_sca_node.avs']);
end

fprintf('%s\n','Locating FEHM initialization (.ini) file...')
inifile=getfile([sourcedir,'*.ini']);

root=inifile(1:end-4);

if nargin<1, finfile_out=[root,'.fin'];end

%Read ini file
[TSP,iniheader]=getini(inifile);

iniheader{3}='   0000000000.000000';

%Read avs file
[avs,avsheader]=getavs(avsfile);

Tindcell = strfind(avsheader, 'Temperature');
Tind = find(~cellfun('isempty', Tindcell),1,'first');

Pindcell = strfind(avsheader, 'Pressure');
Pind = find(~cellfun('isempty', Pindcell),1,'first');

%Replace TSP values with those from avs
TSP(:,1)=avs(:,Tind);
TSP(:,3)=avs(:,Pind);

%OUTPUT
%--------------------------

disp(['Writing output to file: ',finfile_out])
fid=fopen(finfile_out,'w');
fprintf(fid,'%s\n',iniheader{:});
fprintf(fid,'%s','temperature');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',TSP(:,1));
fprintf(fid,'\n%s','saturation');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',TSP(:,2));
fprintf(fid,'\n%s','pressure');
fprintf(fid,'\n%21.10f%25.10f%25.10f%25.10f',TSP(:,3));
fprintf(fid,'\n%s','no fluxes');
fclose(fid);

end