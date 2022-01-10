function fin2ini2 (inifile_out,sourcedir)

%Rewrites .fin file as .ini, zeroing the time header.
%SYNTAX
%   fin2ini2() rewrites a local '.fin' file FILENAME.fin as FILENAME.ini.
%   The initial time (third line of the header) is reset to zero.
%
%   fin2ini2(inifile_out) rewrites a local '.fin' file as 'inifile_out'. The
%   initial time (third line of the header) is reset to zero.
%
%   fin2ini2(inifile_out,sourcedir) instead looks in 'sourcedir' for the
%   source '.fin' file.
%
%
%EXAMPLE
%   fin2ini()
%
%   fin2ini('NewRun.ini')
%
%   fin2ini('new_models/run1/run1.ini','old_models/run12')
%
%   See also GETZONE, MKFEHMDIR, IAP2INI, APPENDZONE.
%
%   Adapted from fin2ini by Tess Weathers, UCSC Hydrogeology
%   Revised 2018/06/07
%       Compatible with .fin files without Temperature, Pressure,
%       or Saturation headers (as found in FEHMv <3.0 or when using WELL)
%       Has not been tested with less than two arguments
%       Compatible with mkfehmdir2
%   
%   Original fin2ini written by Dustin Winslow, UCSC Hydrogeology


%INPUT
%--------------------------
if nargin<3,useiap_outsidezone=0;end
if nargin<2,sourcedir='.';end

if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

fprintf('%s\n','Locating FEHM output (.fin) file...')
finfile=getfile([sourcedir,'*.fin']);

root=finfile(1:end-4);

if nargin<1, inifile_out=[root,'.ini'];end

%READ and REPLACE
%---------------------------
A = regexp( fileread(finfile), '\n', 'split');
A{3} = sprintf('%s','   00000.0000000000');

%WRITE OUTPUT FILE
%---------------------------
fid = fopen([inifile_out], 'w');
fprintf(fid, '%s\n', A{:});
fclose(fid);


end

