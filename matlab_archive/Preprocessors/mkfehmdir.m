function mkfehmdir (root,outdir,sourcedir,useiap,uset0)

%Create a new directory for an FEHM run, copy required and auxillary files
%from mesh directory or a previous run directory, reformatting each where
%appropriate.
%SYNTAX
%   mkfehmdir(root,outdir) copies files from the current directory to a new
%   directory 'ourdir', renaming each to 'root'.EXT while preserving the
%   original file extensions. If a .files file is detected, new run is
%   treated as a restart, changing behavior slightly:
%
%       RESTART CASE .fin is copied to 'outdir' as a .ini file via the
%       fin2ini() function and added to the .files file. The .iap file
%       becomes a required file (generated via ipres()). The .dat file is
%       also copied.
%
%       NON RESTART CASE 'top' and 'bottom' zones are appended to .zone
%       file before copying to 'outdir'. The .files file entry for an .ini
%       file is omitted.
%
%   mkfehmdir(root,outdir,sourcedir) looks for source files in 'sourcedir'
%   instead of current directory.
%
%   mkfehmdir(..., useiap) if set, the new .ini file written will use P
%   values from the .iap file instead of the .fin file - typically used
%   when moving from a conductive run to a coupled one. .iap files are
%   generated with the ipres() function. Default 0.
%
%   mkfehmdir(..., uset0) if set, the new .dat file will use timing
%   information from the previous run as its starting information -
%   typically used when restarting a run that did not finish. Default 0.
%
%EXAMPLE
%   mkfehmdir('z_600_perm_12','perm_12_run');
%   mkfehmdir('3km_run_7','run7','run6');
%
%   See also MKDOTFILES, FIN2INI, APPENDZONE.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.3 , 2014/02/26

if nargin<5, uset0=0;end
if nargin<4, useiap=0;end
if nargin<3,sourcedir='.';end
if ~strcmp(outdir(end),'/'),outdir=[outdir,'/'];end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

%MANAGE DIRECTORIES
%------------------
%Make destination directory
if isdir(outdir)
    fprintf('%s\n',['Directory ''',outdir,''' already exists.'])
    fprintf('%s\n','FILES MAY BE OVERWRITTEN.','Proceed?')
    while 1
        select=input('y/n: ','s');
        if strcmp(select,'y'),break,end
        if strcmp(select,'n'),return,end
    end
else
    fprintf('%s',['Making new directory ''',outdir,''' ... '])
    [stat,mess]=mkdir(outdir);
    if stat
        fprintf('%s\n','Success!')
    else
        fprintf('%s\n',['Failed: ',mess])
        return
    end
end

%Identify type of source directory
fprintf('\n%s\n','Checking for FILES (.files) file...')
if length(dir([sourcedir,'*.files']))<1,
    fprintf('%s\n%s\n\n','No .files file in sourcedir:','NEW RUN IS NOT A RESTART')
    restartflag=0;
else
    fprintf('%s\n%s\n\n','Found .files file in sourcedir:','NEW RUN IS A RESTART')
    restartflag=1;
    
    disp('Checking for FEHM OUTPUT (.fin) file...')
    if length(dir([sourcedir,'*.fin']))<1,
        fprintf('%s\n%s\n\n','No .fin file in sourcedir:','CREATING RESTART FROM .AVS FILE')
        finflag=0;
        
        disp('Specify AVS file to use in creating restart')
        avsfile=getfile([sourcedir,'*_sca_node.avs']);
    else
        fprintf('%s\n%s\n\n','Found .files file in sourcedir:','CREATING RESTART FROM .FIN FILE')
        finflag=1;
        avsfile=0;
    end
end

%LOCATE REQUIRED FILES
%---------------------
sourcefiles={};
outext={};

disp('Locating FEHM (.fehm) file...')
fehmfile=getfile([sourcedir,'*.fehm*']);
sourcefiles=[sourcefiles;{fehmfile}];
outext=[outext;'.fehm'];


disp('Locating STOR (.stor) file...')
storfile=getfile([sourcedir,'*.stor']);
sourcefiles=[sourcefiles;{storfile}];
outext=[outext;'.stor'];


disp('Locating MATERIAL ZONE (.zone) file...')
if ~restartflag
    zonefile=getfile([sourcedir,'*_material.zone']);
else
    zonefile=getfile([sourcedir,'*.zone'],1);
end
sourcefiles=[sourcefiles;{zonefile}];
outext=[outext;'.zone'];


%CHECK FOR SUPPORT FILES

if isempty(dir([sourcedir,'*_outside.zone']))
    disp('No _outside.zone file found, skipping...')
else
    disp('Locating OUTSIDE ZONE (_outside.zone) file...')
    outsidefile=getfile([sourcedir,'*_outside.zone']);
    sourcefiles=[sourcefiles;{outsidefile}];
    outext=[outext;'_outside.zone'];
end

if isempty(dir([sourcedir,'*_material.zone']))
    disp('No _material.zone file found, skipping...')
else
    disp('Locating MATERIAL ZONE (_material.zone) file...')
    materialfile=getfile([sourcedir,'*_material.zone']);
    sourcefiles=[sourcefiles;{materialfile}];
    outext=[outext;'_material.zone'];
end

if isempty(dir([sourcedir,'*.area']))
    disp('No .area file found, skipping...')
else
    disp('Locating AREA (.area) file...')
    areafile=getfile([sourcedir,'*.area']);
    sourcefiles=[sourcefiles;{areafile}];
    outext=[outext;'.area'];
end

if isempty(dir([sourcedir,'*.hfi']))
    disp('No .hfi file found, skipping...')
else
    disp('Locating HEATIN INPUT (.hfi) file...')
    hfifile=getfile([sourcedir,'*.hfi']);
    sourcefiles=[sourcefiles;{hfifile}];
    outext=[outext;'.hfi'];
end

if isempty(dir([sourcedir,'*.iap']))
    disp('No .iap file found, skipping...')
    if restartflag
        error('No .iap file in restart directory. Run IPRES first.')
    end
else
    disp('Locating AMBIENT PRESSURE (.iap) file...')
    iapfile=getfile([sourcedir,'*.iap']);
    sourcefiles=[sourcefiles;{iapfile}];
    outext=[outext;'.iap'];
end

if isempty(dir([sourcedir,'*.ipi']))
    disp('No .ipi file found, skipping...')
else
    disp('Locating IPRES INPUT (.ipi) file...')
    ipifile=getfile([sourcedir,'*.ipi']);
    sourcefiles=[sourcefiles;{ipifile}];
    outext=[outext;'.ipi'];
end

if isempty(dir([sourcedir,'*.rpi']))
    disp('No .rpi file found, skipping...')
else
    disp('Locating ROCKPROP INPUT (.rpi) file...')
    rpifile=getfile([sourcedir,'*.rpi']);
    sourcefiles=[sourcefiles;{rpifile}];
    outext=[outext;'.rpi'];
end


if isempty(dir([sourcedir,'*.rock']))
    disp('No .rock file found, skipping...')
else
    disp('Locating ROCK PROPERTIES (.rock) file...')
    rockfile=getfile([sourcedir,'*.rock']);
    sourcefiles=[sourcefiles;{rockfile}];
    outext=[outext;'.rock'];
end


if isempty(dir([sourcedir,'*.cond']))
    disp('No .cond file found, skipping...')
else
    disp('Locating CONDUCTIVITY (.cond) file...')
    condfile=getfile([sourcedir,'*.cond']);
    sourcefiles=[sourcefiles;{condfile}];
    outext=[outext;'.cond'];
end


if isempty(dir([sourcedir,'*.perm']))
    disp('No .perm file found, skipping...')
else
    disp('Locating PERMEABILITY (.perm) file...')
    permfile=getfile([sourcedir,'*.perm']);
    sourcefiles=[sourcefiles;{permfile}];
    outext=[outext;'.perm'];
end


if isempty(dir([sourcedir,'*.ppor']))
    disp('No .ppor file found, skipping...')
else
    disp('Locating COMPRESSIBILITY (.ppor) file...')
    pporfile=getfile([sourcedir,'*.ppor']);
    sourcefiles=[sourcefiles;{pporfile}];
    outext=[outext;'.ppor'];
end

if isempty(dir([sourcedir,'*.hflx']))
    disp('No .hflx file found, skipping...')
else
    disp('Locating HEATFLUX (.hflx) file...')
    hflxfile=getfile([sourcedir,'*.hflx']);
    sourcefiles=[sourcefiles;{hflxfile}];
    outext=[outext;'.hflx'];
end

if isempty(dir([sourcedir,'*.flow']))
    disp('No .flow file found, skipping...')
else
    disp('Locating TOP_FLOW (.flow) file...')
    flowfile=getfile([sourcedir,'*.flow']);
    sourcefiles=[sourcefiles;{flowfile}];
    outext=[outext;'.flow'];
end

%Lookup table
fprintf('\n%s\n','Specify a lookup table to link to (dialog box).')
[nistfile,nistpath]=uigetfile('.out');
if ~nistfile==0
    disp('Creating static link:')
    fprintf('%s',[outdir,root,'.wpi -> ',nistpath,nistfile,' ... '])
    system(['ln -s ',nistpath,nistfile,' ',outdir,root,'.wpi']);
    fprintf('%s\n\n','Done.')
else
    warning('Invalid file, please create link .wpi file manually.')
end

%COPY AND CREATE FILES
%---------------------
disp('Creating CONTROL (.files) file...')
mkdotfiles(root,[outdir,'fehmn.files'],restartflag);
mkdotfiles(root,[outdir,root,'.files'],restartflag);%for use with old version of gofehml3, remove when all users are up to date

for i=1:length(sourcefiles)
    fprintf('%s',['Copying file: ',sourcefiles{i},' to: ',outdir,root,outext{i},' ... '])
    [stat,mess]=copyfile(sourcefiles{i},[outdir,root,outext{i}]);
    if stat, fprintf('%s\n','Success!')
    else fprintf('%s\n','Failed: ',mess),end
end

if  restartflag
    disp(['Copying .dat file to: ',outdir,root,'.dat,'])
    fprintf('%s\n',['    replacing file names with ''',root,''''])
    datcopy(root,[outdir,root,'.dat'],sourcedir);
    
    if uset0
        [time,deltime]=modeltime(sourcedir,avsfile);
        
        fprintf('\n%s\n',['Initial time set to:     ',num2str(time,'%g')])
        fprintf('%s\n',['Initial timestep set to: ',num2str(deltime,'%g')])
        datreset(time,deltime,[outdir,root,'.dat']);
    end
    
    if finflag
        fprintf('\n%s\n',['Converting .fin file to: ',outdir,root,'.ini'])
        if useiap
            disp('Using IAP file P for all nodes.')
            iap2ini([outdir,root,'.ini'],sourcedir);
        else
            disp('Using IAP file P only at top boundary.')
            fin2ini([outdir,root,'.ini'],sourcedir,'top');
        end
    else
        fprintf('\n%s\n',['Converting ',avsfile,' to ',outdir,root,'.ini'])
        avs2fin([outdir,root,'.ini'],sourcedir,avsfile);
    end
    
else
    fprintf('\n%s\n',['Append ''top'' and ''bottom'' zones from ''',...
        root,'_outside.zone',''' to ''',root,'.zone''?'])
    while 1
        select=input('y/n: ','s');
        if strcmp(select,'y')
            appendzone('top',[outdir,root,'.zone'],outdir);
            appendzone('bottom',[outdir,root,'.zone'],outdir);
            break
        end
        if strcmp(select,'n'),break,end
    end
end

fprintf('\n%s\n','SUGGESTED NEXT STEPS:')
nextsteps={'Run HEATIN to set bottom boundary heat input (check .hfi file).';...
    'Run TOPBC to set constant pressure BC at top nodes (creates .flow file)';...
    'Run ROCKPROP to set rock properties (check .rpi file).';...
    'Run model outside of MATLAB using FEHM (check .dat file).';...
    'Run IPRES to set initial pressure for coupled run (check .ipi file).'};
if restartflag, nextsteps(end)=[];end

fprintf('* %s\n',nextsteps{:});

end