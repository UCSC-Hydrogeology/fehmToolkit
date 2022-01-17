function A=zonetoparea(zones,sourcedir)

%Return the z-area sum for the top nodes within specified zones.
%SYNTAX
%   A = zonetoparea(zones, sourceDir) determines the total z-area exposure
%   of a zone at the top of the model for each zone in the vector 'zones'.
%   Returns a vector 'A', containing sums for each zone in m^2.
%
%EXAMPLE
%   A = zonetoparea([3,4], '.')
%
%   See also GETNODE, GETZONE.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.3, 2014/06/10

if nargin<1,error('Must specify zone number(s).');end
if nargin<2,sourcedir='./';end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

%Locate files
%------------

disp('Locating OUTSIDE ZONE (_outside.zone) file...')
outsidefile=getfile([sourcedir,'*outside.zone']);

disp('Locating ZONE (*.zone) file...')
zonefile=getfile([sourcedir,'*.zone'],1);

disp('Locating AREA (.area) file...')
areafile=getfile([sourcedir,'*.area']);

%Gather node numbers
%-------------------
fprintf('\n%s%s\n','Reading file: ',outsidefile)
node_top=getzone('top',outsidefile);

fprintf('%s%s\n','Reading file: ',areafile)
area_top=getzone('top',areafile);


%Parse node numbers
%------------------
A=zeros(length(zones),1);
for i=1:length(zones)
    fprintf('%s%u\n','Reading zone: ',zones(i))
    node_zone=getzone(zones(i),zonefile);
    [~,~,ib]=intersect(node_zone,node_top);
    area_zonetop=area_top(ib,3);
    A(i)=sum(area_zonetop);
end



end