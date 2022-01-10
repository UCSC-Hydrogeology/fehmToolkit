function zonetemp(zones,temps,sourcedir)

%Rewrites temperature values in a .fin file by zone, writing output into a
%new .fin file.
%SYNTAX
%   zonetemp(zones,temps) overwrites the temperatures from a local '.fin'
%   file FILENAME1.fin with temperatures and zones contained in 'zones' and
%   'temps' inputs. The new file is written as FILENAME2.fin, where an
%   informative string has been appended to the file name. 'Zones' and
%   'temps' can be single numbers, or vectors of equal length.
%
%   zonetemp(zones,temps,sourcedir) instead looks in 'sourcedir' for the
%   source '.fin' and '.zone' files.
%
%EXAMPLE
%   zonetemp(3,64.5)
%
%   zonetemp([1:4],[2,10,64.5,18],'../run12')
%
%   See also GETZONE, IPRES, IAP2INI, FIN2INI.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2014/05/29

%INPUT
%--------------------------

if nargin<3,sourcedir='.';end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

if length(zones)~=length(temps)
    error('Zones and temps must be vectors of the same length.')
end

fprintf('%s\n','Locating FEHM output (.fin) file...')
finfile=getfile([sourcedir,'*.fin']);

fprintf('%s\n','Locating ZONE (.zone) file...')
zonefile=getfile([sourcedir,'*.zone'],1);

root=finfile(1:end-4);

%Read fin file
[TSP,header]=getfin(finfile);

for i=1:length(zones)
    nodes=getzone(zones(i),zonefile);
    TSP(nodes,1)=temps(i);
end


%OUTPUT
%--------------------------
ztstr=sprintf('_Z%uT%1.0f',[zones(:),temps(:)]');
finfile_out=[root,ztstr,'.fin'];

disp(['Writing output to file: ',finfile_out])
fid=fopen(finfile_out,'w');
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