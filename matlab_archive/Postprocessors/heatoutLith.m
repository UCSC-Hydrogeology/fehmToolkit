function heatin(nodefile,hfi_in,source_dir)

%Calculates and writes heat input at base of model (.hflx file) using
%parameters from .hfi file.
%SYNTAX
%   heatin() reads a local '.hfi' file FILENAME.hfi and uses functions
%   within to calculate the total heat input (MW) for each bottom node from
%   a local '_outside.zone' file. Writes output to '.hflx' file
%   FILENAME.hflx. Reads back and plots '.hflx' output for verification.
%
%   heatin(hfi_in) instead reads 'hfi_in' as the input '.hfi' file. Output
%   will use the same root as 'hfi_in', with the '.hflx' extension.
%
%FORMAT
%   Heatflux input files (.hfi) use MATLAB syntax, and may use any number
%   of commented lines as a header. heatin() will execute any lines
%   verbatim that are found between the 'hflx' and 'stop' flags.
%
%   This block must contain a final function named "HFLX", but may contain
%   any number of subfunctions. HFLX must at least be a function of x, y,
%   and z, even if some or all of these dependencies are null.
%
%   Use ALL CAPS for all variable or function definitions, to avoid
%   confusion with the main program.
%
%EXAMPLE
%   heatin();
%   heatin('NewRun.hfi');
%
%   See also IPRES, ROCKPROP, HEATOUT.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/21

%INPUT
%----------------------

disp('Locating outsize zone (_outside.zone) file...')
outsidefile=getfile('*_outside.zone');

disp('Locating FEHM (.fehm) file...')
fehmfile=getfile('*.fehm*');

if nargin < 2,
    disp('Locating heatflux in (.hfi) file...')
    hfifile=getfile('*.hfi');
else
    hfifile=hfi_in;
end

if nargin<3,sourcedir='./';end

disp('Locating area (.area) file...')
areafile=getfile('*.area');

%Generate top node list & area table
disp(['Reading file: ',outsidefile])
node=getzone('top',outsidefile);

disp(['Reading file: ',areafile])
area=getzone('top',areafile);

%Determine node coordinates
disp(['Reading file: ',fehmfile])
coor=node2coor(node,fehmfile);

%Read age and q functions from .hfi file
disp(['Reading file: ',hfifile])
fid=fopen(hfifile);
hfi=textscan(fid,'%s','Delimiter','\n');
fclose(fid);
hfi=hfi{1};

% Read in custom node list and extract areas from previously loaded top 
% area and node file
disp('Locating node (.nodes.zone) file...')
outsidefile=getfile([sourcedir,nodefile]);
    
if nargin == 1,
    disp('Locating node (.nodes.zone) file...')
    prompt = 'What is the name of the zone? (enter with no quotes) ';
    zonename = input(prompt,'s');
    topnode=getzone(zonename,outsidefile);
end

% Extract the areas of the custom nodes from the top area file
custom_index = ismember(node,topnode);
custom_node = node(custom_index);
custom_area = area(custom_index,3);
custom_coor = node2coor(custom_node);



%CALCULATION
%-------------------------
%Define functions from .hfi file
start_ind=find(strcmp('hflx',hfi),1,'first')+1;
end_ind=find(strcmp('stop',hfi),1,'first')-1;

for i=start_ind:end_ind, eval([hfi{i}]);end

%Calculate heatflow for each node
fprintf('%s\n','Calculating heatflow using:',outsidefile,areafile,fehmfile,hfifile)
q=-abs(custom_area.*HFLX(custom_coor(:,1),custom_coor(:,2),custom_coor(:,3)));

disp(['Total heat input (MW): ',num2str(sum(q))])




%PLOT
%-----------------------------

heatmapPoly(custom_coor,abs((q*10.^6)./custom_area)); %Convert to W/m^2
title('Heat output W/m^2')
axis equal;

end