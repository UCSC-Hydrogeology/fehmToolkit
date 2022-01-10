function Q=Qout(sourceDir,lastFlag)

%Read model output, returning a structure of basic model output.
%SYNTAX
%   Q = Qout(sourceDir) reads information from a variety of files within an
%   FEHM run directory. Returns heat and fluid input and output, node
%   numbers, and areas for top and bottom boundaries, as well as vector
%   information throughout the model. All values are returned via the
%   structure Q.
%
%   Q = Qout(..., lastflag) uses the .avs file with the highest number, if
%   lastflag is set.
%
%EXAMPLE
%   Q = Qout('.', 1);
%
%   See also MODELTIME, HISTCHK, HEATOUT.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.3, 2015/07/23
%   Revision: 1.31, A. Fisher, 2020/11/11 - calculate flow from BB

if nargin<1,sourceDir='./';end
if ~strcmp(sourceDir(end),'/'),sourceDir=[sourceDir,'/'];end
if nargin<2,lastFlag=0;end

fprintf('%s\n','Locating FEHM output (.avs) file...')
avsFile=getfile([sourceDir,'*sca_node.avs'],0,0,lastFlag);
vecFile=[avsFile(1:end-12),'vec_node.avs'];

%Locate files
%------------
fprintf('%s\n','Locating OUTSIDE ZONE (_outside.zone) file...')
outsideFile = getfile([sourceDir,'*outside.zone']);

fprintf('%s\n','Locating FEHM (.fehm) file...')
fehmFile = getfile([sourceDir,'*.fehm*']);

fprintf('%s\n','Locating AREA (.area) file...')
areaFile = getfile([sourceDir,'*.area']);

disp('Locating conductivity (.cond) file...')
condFile = getfile([sourceDir,'*.cond']);

disp('Locating HEATFLUX (.hflx) file...')
hflxFile = getfile([sourceDir,'*.hflx']);

%Gather node numbers
%-------------------
disp('Reading node numbers and zones...')
nodeTop = getzone('top', outsideFile);
areaTop = getzone('top', areaFile);

nodeBelowTop = getnodebelow(nodeTop, fehmFile);

nodeBot = getzone('bottom', outsideFile);
areaBot = getzone('bottom', areaFile);

%Read simulation output
%----------------------
[avs, avsHeader] = getavs(avsFile);
vec = getavs(vecFile);

Scol = find(...
    cellfun(@(in) ~isempty(strfind(in, 'Source')), avsHeader),...
    1, 'first');
Tcol = find(...
    cellfun(@(in) ~isempty(strfind(in, 'Temperature')), avsHeader),...
    1, 'first');

cond = getprop(condFile);
hflx = gethflx(hflxFile);

%Calculation
%-----------
coorTopAll = node2coor([nodeTop; nodeBelowTop], fehmFile);
coorTopAll = round(1e3 .* coorTopAll) ./ 1e3;%round to nearest mm for interpolation
coorTop = coorTopAll(1:length(nodeTop),:);
coorBelowTop = coorTopAll(length(nodeTop)+1:end,:);
clearvars coorTopAll

fprintf('%s\n','Calculating seafloor heatflow (mW/m2):')
qTop = -2 .* cond(nodeTop, 3) .* cond(nodeBelowTop, 3) ./ ...
    (cond(nodeTop, 3) + cond(nodeBelowTop, 3)) .* ...
    (avs(nodeTop, Tcol) - avs(nodeBelowTop, Tcol)) ./ ...
    (coorTop(:,3) - coorBelowTop(:,3));

%Save to structure
%-----------------
Q.qTop = qTop .* 1000;%mW conversion
Q.qBot = hflx ./ areaBot(:, 3) ./ 1e6;%mW conversion

Q.ATop = areaTop(:, 3);
Q.ABot = areaBot(:, 3);

Q.qTopTot = sum(areaTop(:, 3) .* qTop ./ 1e6);%MW conversion
Q.qBotTot = sum(hflx);%in MW

Q.nodeTop = nodeTop;
Q.nodeBot = nodeBot;

Q.vec = vec;

Q.S = avs(:, Scol);
Q.SOut = sumpos(Q.S);
Q.SIn = sumpos(-Q.S);

Q.STop = avs(nodeTop, Scol);
Q.STopOut = sumpos(Q.STop);
Q.STopIn = -sumpos(-Q.STop);
% AF 20/11/11
Q.SBB=sum([Q.S(158722) Q.S(173437)  Q.S(173438) Q.S(188153) Q.S(188154) Q.S(203302) Q.S(203303) Q.S(203304) Q.S(203308)]);
%
Q.SBot = avs(nodeBot, Scol);
Q.SBotOut = sumpos(Q.SBot);
Q.SBotIn = -sumpos(-Q.SBot);

end