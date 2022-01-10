function datreset (t0,delt0, datfile)

%Reset the initial time and timestep in 'datfile' to 'to' and 'delt0'.
%SYNTAX
%   datreset(t0, delt0) replaces the initial timestep in a .dat file found in
%   the current directory with 'delt0'.
%
%   datreset(t0, delt0, datfile) specified the .dat file to be modified.
%
%EXAMPLE
%   datcopy(0, 7300, 'testrun.dat')
%
%   See also DATCOPY, MKFEHMDIR, MKDOTFILES, FIN2INI, IAP2INI.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2014/01/13

if ~ischar(t0),t0=num2str(t0,'%g');end
if ~ischar(delt0),delt0=num2str(delt0,'%g');end

if nargin<3
    disp('Locating FEHM input (.dat) file...')
    datfile=getfile('*.dat');
end

%INPUT
%--------------------
disp(['Reading file: ',datfile])
fid=fopen(datfile);
datlines=textscan(fid,'%s','Delimiter','\n');
fclose(fid);
datlines=datlines{:};

%REPLACE FILENAMES
%--------------------
timeind=find(strcmp('time',datlines),1,'first')+1;
timecell=textscan(datlines{timeind},'%s');
timecell=timecell{:};

timecell{1}=delt0;
timecell{7}=t0;
datlines{timeind}=sprintf('%s ',timecell{:});

%OUTPUT
%-------------------
disp(['Writing file: ',datfile])
fid=fopen(datfile,'w');
fprintf(fid,'%s\n',datlines{:});
fclose(fid);

end