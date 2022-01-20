function rockprop(rpi_in)

%Calculates and writes rock properties (.cond, .perm, .ppor, .rock files)
%using parameters from .rpi file.
%SYNTAX
%   rockprop() reads a local '.rpi' file FILENAME.rpi and uses functions
%   within to calculate rock properties for each node in the local .fehm
%   file. Writes output to files FILENAME.EXT for each file type (.cond,
%   .perm, .ppor, .rock).
%
%   rockprop(rpi_in) instead reads 'rpi_in' as the input '.rpi' file. Output
%   will use the same root as 'rpi_in', with the appropriate extensions.
%
%FORMAT
%   MATLAB syntax is used in rock property input files (.rpi), allowing any
%   number of commented lines as a header.
%
%   rockprop() will execute any lines verbatim that are found between the
%   PROPERTY and PROPERTYstop flags, all lowercase (e.g. 'conductivity',
%   'conductivitystop').
%
%   'stop' statements which separate the code into 'blocks' and allows
%   properties to be assigned separately to each set of zones.
%
%   ZONES must be defined in each block an integer vector. This determines
%   which zones will use the property function 'FUN' defined in this block.
%
%   'FUN' must be defined in each block as a function for property
%   assignments. FUN may contain any number of subfunctions and must at
%   least be a function of 'depth' and 'porosity', even if these
%   dependencies are null.
%
%   The porosity property block MUST COME FIRST, as it is used in other
%   property assignments. FUN in the porosity block must at least be a
%   function of 'depth', even if this dependency is null.
%
%   Use ALL CAPS for all variable or function definitions, to avoid
%   confusion with the main program. Only 'depth' and 'porosity' are the
%   only lowercase variables used (as they also exist in the main code),
%   and should NEVER be defined directly within the .rpi file.
%
%   ANISOTROPY is a 3-element vector which defines anisotropy for
%   conductivity and permeability. This is not a required call, and
%   defaults to isotropic: [1,1,1].
%
%   The compressibility section must include definitions in each zone for
%   both grain density and specific heat of grains. These values are
%   required for output to the .rock file, and may also be used to define
%   'FUN' in the compressiblity block.
%       Use 'RHOG' for grain density.
%       Use 'SPECHEAT' for specific heat of grains.
%
%EXAMPLE
%   rockprop();
%   heatin('rockprop.rpi');
%
%   See also IPRES, HEATIN, HEATOUT.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2013/09/19

%INPUT
%--------------------------

disp('Locating FEHM (.fehm) file...')
fehmfile=getfile('*.fehm*');

disp('Locating outsize zone (_outside.zone) file...')
outsidefile=getfile('*outside.zone');

disp('Locating material zone (.zone) file...')
zonefile=getfile('*.zone',1);

if nargin<1
    fprintf('%s\n\n','Locating rockprop input (.rpi) file...')
    root=getfile('*.rpi');
else
    root=rpi_in;
end

%Read .fehm(n)
fprintf('%s\t%s\n','Reading file: ',fehmfile)
[node,coor]=getnode(fehmfile);
coor=round(1e3.*coor)./1e3;%round to nearest mm for interpolation

%Read outside.zone
fprintf('%s\t%s\n','Reading file: ',outsidefile)
node_sflr=getzone('top',outsidefile);
coor_sflr=coor(node_sflr,:);

%Identify .zone file
fprintf('%s\t%s\n','Reading file: ',zonefile)

%Read .rpi
root=root(1:end-4);
fprintf('%s\t%s\n\n','Reading file: ',[root,'.rpi'])
fid=fopen([root,'.rpi']);
rpi=textscan(fid,'%s','Delimiter','\n');
fclose(fid);
rpi=rpi{1};

%INTERPOLATION
%-------------------------
plane=0;
if length(unique(coor(:,1)))==1, plane=1;end
if length(unique(coor(:,2)))==1, plane=2;end

if plane%   WORKING IN 2D
    %Create false 3D by replicating grid into 3 parallel slices
    disp('Grid is 2D, replicating grid for false 3D required for interpolation...')
    coor_sflr_3d=repmat(coor_sflr,3,1);
    coor_sflr_3d(:,plane)=coor_sflr_3d(:,plane)+[10+zeros(length(node_sflr),1);zeros(length(node_sflr),1);-10+zeros(length(node_sflr),1)];
    coor_3d=repmat(coor,3,1);
    coor_3d(:,plane)=coor_3d(:,plane)+[10+zeros(length(node),1);zeros(length(node),1);-10+zeros(length(node),1)];
else%       WORKING IN 3D
    coor_sflr_3d=coor_sflr;
    coor_3d=coor;
end

disp('Determining depths below seafloor...')
%Make a seafloor interpolant for depth
sflr_interp = scatteredInterpolant(coor_sflr_3d(:,1),coor_sflr_3d(:,2),coor_sflr_3d(:,3),'linear','nearest');

%Determine node depths below seafloor
depth=sflr_interp(coor_3d(:,1),coor_3d(:,2))-coor_3d(:,3);

%PROPERTY ASSIGNMENT
%------------------------------

%Initialize property arrays
porosity=zeros(size(node))-1;
compressibility=porosity;
graindensity=porosity;
specificheat=porosity;
conductivity=repmat(porosity,1,3);%conductivity and permeability arrays are larger to allow anisotropy
permeability=conductivity;

%Porosity
%********
disp('Assigning porosity...')
%Identify breakpoints around equation definitions
breaks=[find(strcmp('porosity',rpi),1,'first');find(strcmp('stop',rpi));find(strcmp('porositystop',rpi))];
breaks(breaks > breaks(end) | breaks < breaks(1))=[];%remove stops not associated with property

for j=1:length(breaks)-1%loop over each equation definition
    clearvars FUN ZONES
       
    for k=breaks(j)+1:breaks(j+1)-1, eval(rpi{k});end%define function from .rpi
    
    if exist('FUN','var')
        %Build list of nodes in specified zones
        zone_nodes=[];
        for k=1:length(ZONES),zone_nodes=[zone_nodes;getzone(ZONES(k),zonefile)];end
        
        %Assign properties in specified zones, according to defined functions
        porosity(zone_nodes)=FUN(depth(zone_nodes));
        
    else
        warning('RockProp:MissingFunction',['No function defined in lines (',num2str(breaks(j)+1),'-',num2str(breaks(j+1)-1),') of ',root,'.rpi - skipping section...'])
    end
end

if ~isempty(porosity(porosity<0)), warning('RockProp:UndefinedPorosity','Some nodes remain undefined: assigning -1 to empty values. Check ZONES definition in .rpi'),end

%Conductivity
%************
disp('Assigning conductivity...')
%Identify breakpoints around equation definitions
breaks=[find(strcmp('conductivity',rpi),1,'first');find(strcmp('stop',rpi));find(strcmp('conductivitystop',rpi))];
breaks(breaks > breaks(end) | breaks < breaks(1))=[];%remove stops not associated with property

for j=1:length(breaks)-1%loop over each equation definition
    clearvars FUN ZONES
    ANISOTROPY=[1,1,1];%default value for anisotropy
    
    for k=breaks(j)+1:breaks(j+1)-1, eval(rpi{k});end%define function from .rpi
    
    if exist('FUN','var')
        %Build list of nodes in specified zones
        zone_nodes=[];
        for k=1:length(ZONES),zone_nodes=[zone_nodes;getzone(ZONES(k),zonefile)];end
        
        %Assign properties in specified zones, according to defined functions, applying anisotropy
        cond=FUN(depth(zone_nodes),porosity(zone_nodes));
        for k=1:3,conductivity(zone_nodes,k)=ANISOTROPY(k).*cond;end
        
    else
        warning('RockProp:MissingFunction',['No function defined in lines (',num2str(breaks(j)+1),'-',num2str(breaks(j+1)-1),') of ',root,'.rpi - skipping section...'])
    end
end

if ~isempty(conductivity(conductivity<0)), warning('RockProp:UndefinedConductivity','Some nodes remain undefined: assigning -1 to empty values. Check ZONES definition in .rpi'),end

%Permeability
%************
disp('Assigning permeability...')
%Identify breakpoints around equation definitions
breaks=[find(strcmp('permeability',rpi),1,'first');find(strcmp('stop',rpi));find(strcmp('permeabilitystop',rpi))];
breaks(breaks > breaks(end) | breaks < breaks(1))=[];%remove stops not associated with property

for j=1:length(breaks)-1%loop over each equation definition
    clearvars FUN ZONES
    ANISOTROPY=[1,1,1];%default value for anisotropy
    
    for k=(breaks(j)+1):(breaks(j+1)-1),eval(rpi{k});end%define function from .rpi
    
    if exist('FUN','var')
        %Build list of nodes in specified zones
        zone_nodes=[];
        for k=1:length(ZONES),zone_nodes=[zone_nodes;getzone(ZONES(k),zonefile)];end
        
        %Assign properties in specified zones, according to defined functions, applying anisotropy
        perm=FUN(depth(zone_nodes),porosity(zone_nodes));
        for k=1:3,permeability(zone_nodes,k)=ANISOTROPY(k).*perm;end
        
    else
        warning('RockProp:MissingFunction',['No function defined in lines (',num2str(breaks(j)+1),'-',num2str(breaks(j+1)-1),') of ',root,'.rpi - skipping section...'])
    end
end

if ~isempty(permeability(permeability<0)), warning('RockProp:UndefinedPermeability','Some nodes remain undefined: assigning -1 to empty values. Check ZONES definition in .rpi'),end

%Compressibility
%***************
disp('Assigning compressibility...')
%Identify breakpoints around equation definitions
breaks=[find(strcmp('compressibility',rpi),1,'first');find(strcmp('stop',rpi));find(strcmp('compressibilitystop',rpi))];
breaks(breaks > breaks(end) | breaks < breaks(1))=[];%remove stops not associated with property

for j=1:length(breaks)-1%loop over each equation definition
    clearvars FUN ZONES
        
    for k=breaks(j)+1:breaks(j+1)-1, eval(rpi{k});end%define function from .rpi
    
    if exist('FUN','var')
        %Build list of nodes in specified zones
        zone_nodes=[];
        for k=1:length(ZONES),zone_nodes=[zone_nodes;getzone(ZONES(k),zonefile)];end
        
        %Assign properties in specified zones, according to defined functions
        compressibility(zone_nodes)=FUN(depth(zone_nodes),porosity(zone_nodes));
        graindensity(zone_nodes)=RHOG;
        specificheat(zone_nodes)=SPECHEAT;
        
    else
        warning('RockProp:MissingFunction',['No function defined in lines (',num2str(breaks(j)+1),'-',num2str(breaks(j+1)-1),') of ',root,'.rpi - skipping section...'])
    end
end

if ~isempty(compressibility(compressibility<0)), warning('RockProp:UndefinedCompressibility','Some nodes remain undefined: assigning -1 to empty values. Check ZONES definition in .rpi'),end
if ~isempty(graindensity(graindensity<0)), warning('RockProp:UndefinedGrainDensity','Some nodes remain undefined: assigning -1 to empty values. Check ZONES definition in .rpi'),end
if ~isempty(specificheat(specificheat<0)), warning('RockProp:UndefinedSpecificHeat','Some nodes remain undefined: assigning -1 to empty values. Check ZONES definition in .rpi'),end

%OUTPUT
%------------------------------

%Format arrays for output
[node,order]=sort(node);
porosity=porosity(order);
graindensity=graindensity(order);
specificheat=specificheat(order);
compressibility=compressibility(order);
conductivity=conductivity(order,:);
permeability=permeability(order,:);

%.ROCK file
%**********
%Build output
fprintf('\n%s\t%s\n','Writing file: ',[root,'.rock'])
outputstring=sprintf('%s\n','rock');

newline=1;
for i=1:length(node)
    if newline,%set lower and upper node bounds for output
        lower=node(i);
        upper=lower;
        graindensityout=graindensity(i);
        specificheatout=specificheat(i);
        porosityout=porosity(i);
        
        newline=0;
    end
    
    if i==length(node)%if last node, automatically end line
        newline=1;
    else
        if (node(i)+1==node(i+1)...
                && strcmp(sprintf('%13.5E',graindensity(i+1)),sprintf('%13.5E',graindensityout))...
                && strcmp(sprintf('%13.5E',specificheat(i+1)),sprintf('%13.5E',specificheatout))...
                && strcmp(sprintf('%13.5E',porosity(i+1)),sprintf('%13.5E',porosityout)))
            upper=upper+1;
        else newline=1;
        end
    end
    
    if newline, outputstring=[outputstring,sprintf('%7u %7u %1u\t%13.5E\t%13.5E\t%13.5E\n',lower,upper,1,graindensityout,specificheatout,porosityout)];end
end
outputstring=[outputstring,sprintf('%s\n','')];

fid=fopen([root,'.rock'],'w');
fprintf(fid,'%s',outputstring);
fclose(fid);
clearvars outputstring

%.COND file
%**********
%Build output
fprintf('%s\t%s\n','Writing file: ',[root,'.cond'])
fid=fopen([root,'.cond'],'w');
fprintf(fid,'%s\n','cond');

newline=1;
for i=1:length(node)
    if newline,%set lower and upper node bounds for output
        lower=node(i);
        upper=lower;
        condxout=conductivity(i,1);
        condyout=conductivity(i,2);
        condzout=conductivity(i,3);
        
        newline=0;
    end
    
    if i==length(node)%if last node, automatically end line
        newline=1;
    else
        if (node(i)+1==node(i+1)...
                && strcmp(sprintf('%13.5E',conductivity(i+1,1)),sprintf('%13.5E',condxout))...
                && strcmp(sprintf('%13.5E',conductivity(i+1,2)),sprintf('%13.5E',condyout))...
                && strcmp(sprintf('%13.5E',conductivity(i+1,3)),sprintf('%13.5E',condzout)))
            upper=upper+1;
        else newline=1;
        end
    end
    
    if newline, fprintf(fid,'%7u %7u %1u\t%13.5E\t%13.5E\t%13.5E\n',lower,upper,1,condxout,condyout,condzout);end
end
fprintf(fid,'%s\n','');
fclose(fid);

%.PERM file
%**********
%Build output
fprintf('%s\t%s\n','Writing file: ',[root,'.perm'])
fid=fopen([root,'.perm'],'w');
fprintf(fid,'%s\n','perm');

newline=1;
for i=1:length(node)
    if newline,%set lower and upper node bounds for output
        lower=node(i);
        upper=lower;
        permxout=permeability(i,1);
        permyout=permeability(i,2);
        permzout=permeability(i,3);
        
        newline=0;
    end
    
    if i==length(node)%if last node, automatically end line
        newline=1;
    else
        if (node(i)+1==node(i+1)...
                && strcmp(sprintf('%13.5E',permeability(i+1,1)),sprintf('%13.5E',permxout))...
                && strcmp(sprintf('%13.5E',permeability(i+1,2)),sprintf('%13.5E',permyout))...
                && strcmp(sprintf('%13.5E',permeability(i+1,3)),sprintf('%13.5E',permzout)))
            upper=upper+1;
        else newline=1;
        end
    end
    
    if newline, fprintf(fid,'%7u %7u %1u\t%13.5E\t%13.5E\t%13.5E\n',lower,upper,1,permxout,permyout,permzout);end
end
fprintf(fid,'%s\n','');
fclose(fid);

%.PPOR file
%**********
%Build output
fprintf('%s\t%s\n','Writing file: ',[root,'.ppor'])
fid=fopen([root,'.ppor'],'w');
fprintf(fid,'%s\n%4i\n','ppor',1);

newline=1;
for i=1:length(node)
    if newline,%set lower and upper node bounds for output
        lower=node(i);
        upper=lower;
        compressibilityout=compressibility(i);
                
        newline=0;
    end
    
    if i==length(node)%if last node, automatically end line
        newline=1;
    else
        if (node(i)+1==node(i+1) && strcmp(sprintf('%13.5E',compressibility(i+1)),sprintf('%13.5E',compressibilityout)))
            upper=upper+1;
        else newline=1;
        end
    end
    
    if newline, fprintf(fid,'%7u %7u %1u\t%13.5E\n',lower,upper,1,compressibilityout);end
end
fprintf(fid,'%s\n','');
fclose(fid);

end
