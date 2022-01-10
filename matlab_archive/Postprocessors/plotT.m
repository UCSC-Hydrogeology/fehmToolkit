function plotT(sy,xlimit,ylimit,tlim,interpmethod,sourcedir,lastflag)

%Plot model temperature along a plane with constant y-value. Code should be
%modified to allow more generic planar cross-sections.
%SYNTAX
%   plotT(sy) plots temperature along a plane with y = sy, interpolating as
%   necessary.
%
%   plotT(sy, xlimit, ylimit, tlimit) allows x, y, and temperature bounds
%   to be set for the plot.
%
%   plotT(..., interpmethod) sets the interpolation method. See
%   documentation for TriScatteredInterp for details.
%
%   plotT(..., sourcedir) specifies the model directory.
%
%   plotT(..., lastflag) uses the .avs file with the highest number, if
%   lastflag is set.
%
%EXAMPLE
%   plotT(20000, [0, 1e4], [0, 1e5], [0, 100], 'nearest', '.', 1);
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.2, 2015/07/23

if ~exist('lastflag','var'), lastflag=0;end
if ~exist('sourcedir','var'),sourcedir='./';end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

if nargin<1, error('Must specify sy.'),end
if ~exist('interpmethod','var'), interpmethod='nearest';end

%INPUT
disp('Locating FEHM (.fehm) file...')
fehmfile=getfile([sourcedir,'*.fehm*']);

disp('Locating scalar node (_sca_node) file...')
scafile=getfile([sourcedir,'*_sca_node*'],0,0,lastflag);

[avs,avsheader]=getavs(scafile);
Tcol=find(cellfun(@(in)~isempty(strfind(in,'Temperature')),avsheader),1,'first');

T=avs(:,Tcol);

fprintf('%s\t%s\n','Reading file: ',fehmfile)
[node,coor]=getnode(fehmfile);
coor=round(coor);

xlims=[min(coor(:,2)),max(coor(:,2))];
ylims=[min(coor(:,3)),max(coor(:,3))];

slice=node(coor(:,1)==sy);
if isempty(slice), error('No nodes along sy, try another slice.');end
coor=coor(slice,:);
T=T(slice);

%PLOTTING
disp('Generating plots...')

yres=2000;
zres=1000;

g=TriScatteredInterp(coor(:,2),coor(:,3),T,interpmethod);

y=min(coor(:,2)):(max(coor(:,2))-min(coor(:,2)))/yres:max(coor(:,2));
z=min(coor(:,3)):(max(coor(:,3))-min(coor(:,3)))/zres:max(coor(:,3));

[y,z]=meshgrid(y,z);

T=flipud(g(y,z));

imagesc(xlims,ylims,T);
colormap('Jet');
colorbar('South');
xlabel('x');ylabel('z');title('Temperature (degC)');
if exist('xlimit','var'),xlim(xlimit);end
if exist('ylimit','var'),ylim(ylimit);end
if exist('tlim','var'), caxis(tlim);end

end