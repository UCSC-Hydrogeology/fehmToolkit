function [time,deltime]=modeltime(sourcedir,avsfile)

%Calculate and return model-time run-time and time-step size.
%
%SYNTAX
%   [time, deltime] = modeltime(sourcedir) returns the runtime in model
%   time for a given directory using the .hist file, and the timestep size
%   at the end of the run.
%   
%   [time, deltime] = modeltime(sourcedir, avsfile) if an avs file is
%   specified, time and deltime are instead calculated for when a
%   particular .avs file was written.
%
%EXAMPLE
%   [time, deltime] = modeltime('run17_r1', 'run17_r1.00005_sca_node.avs')
%
%   See also HISTCHK, MKFEHMDIR, GETHIST.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2014/03/05

if nargin<1,sourcedir='.';end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

if nargin<2 || ~ischar(avsfile);
    avsflag=0;
else
    avsflag=1;
end

disp('Locating FEHM history (.hist) file...')
histfile=getfile([sourcedir,'*.hist']);
his=gethist(histfile,1,0);

if avsflag
    if ~ischar(avsfile)
        fprintf('%s\n','Locating scalar node (_sca_node.avs) file...')
        avsfile=getfile([sourcedir,'*_sca_node.avs']);
    end
    
    %Determine avs output #
    avsdot=strfind(avsfile,'.');
    avsroot=avsfile(avsdot(end-1)+1:avsdot(end)-1);
    avsund=strfind(avsroot,'_');
    
    avsnum=str2double(avsroot(1:avsund(1)-1));
    
    %Determine timesteps per output
    disp('Locating FEHM input (.dat) file...')
    datfile=getfile([sourcedir,'*.dat']);
    disp(['Reading file: ',datfile])
    fid=fopen(datfile);
    datwords=textscan(fid,'%s');
    fclose(fid);
    datwords=datwords{:};
    
    step_ind=find(strcmp('avs',datwords),1,'first')+1;
    stepsize=str2double(datwords{step_ind});
    
    step=min(length(his.deltime),(avsnum-1).*stepsize);
else
    step=length(his.deltime);
end

time=his.time(step+1);
deltime=his.deltime(step);

end