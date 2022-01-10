function datcopy (root, datfile_out, sourcedir)

%Copy an FEHM dat file, replacing all root filename instances with 'root'.
%
%SYNTAX
%   datcopy( root , datfile_out ) copies a .dat file found in the current
%   directory to the filename and location specified by datfile_out. During
%   this copy, root filenames in each 'file' macro call are replaced with
%   'root'.
%   
%   datcopy( root , datfile_out , sourcedir ) looks for source files in
%   'sourcedir' instead of current directory.
%
%EXAMPLE
%   datcopy('run17_r1','run17_r1.dat','../run17')
%
%   See also DATRESET, MKFEHMDIR, MKDOTFILES, FIN2INI, IAP2INI.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/09/16

if nargin<3,sourcedir='.';end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

%INPUT
%--------------------
disp('Locating FEHM input (.dat) file...')
datfile=getfile([sourcedir,'*.dat']);

disp(['Reading file: ',datfile])
fid=fopen(datfile);
datlines=textscan(fid,'%s','Delimiter','\n');
fclose(fid);
datlines=datlines{:};

%REPLACE FILENAMES
%--------------------
fileind=find(strcmp('file',datlines))+1;
swaproot=@(str_in)[root,str_in(strfind(str_in,'.'):end)];

datlines(fileind)=cellfun(swaproot,datlines(fileind),'UniformOutput',0);

%OUTPUT
%-------------------
disp(['Writing file: ',datfile_out])
fid=fopen(datfile_out,'w');
fprintf(fid,'%s\n',datlines{:});
fclose(fid);

end