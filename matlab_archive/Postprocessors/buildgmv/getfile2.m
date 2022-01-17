function file = getfile2(search,zonefileflag,batchflag)

%Search for file or directory name using wildcards.
%SYNTAX
%   file = getfile(search) returns the path and file name matching 'search',
%   a string including wildcards. If multiple matches exist, the user is
%   prompted.
%
%   file = getfile(search, zonefileflag) ignores files ending in
%   "_outside.zone" if 'zonefileflag' is non-zero. This can avoid being
%   propted when searching for a "*.zone" file.
%
%   file = getfile(search, zonefileflag, batchflag) returns a cell array
%   containing all matches instead of prompting the user if 'batchflag' is
%   non-zero.
%
%EXAMPLES
%   file = getfile('*.fehm*');
%   file = getfile('Gridfolder/Grid2/*.zone',1);
%   file = getfile('*sca_node*',0,1);
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/18
%   Revision: 1.01, 2013/02/26 by A. Fisher: return 'nofile' if no file

if nargin<2, zonefileflag=0;end
if nargin<3, batchflag=0;end

%Generate list of files in folder
filelist=dir(search);
filelist={filelist.name}';

if zonefileflag,
    rm=[];
    for i=1:length(filelist)
        if strfind(filelist{i},'_outside.zone'), rm=[rm,i];end
    end
    filelist(rm)=[];
end

% Replace next line so that we get a file name of 'nofile' of the file does
% not exist. This is useful for having the option of addiing additional
% files. 
% AF 2013/02/26
%
%if isempty(filelist), error(['No files matching ''',search,''' exist in specified location.']);end
if isempty(filelist), file='nofile';end

%Select file
if length(filelist)==1, file=filelist{1};
else
    if batchflag, file=filelist;
    else
        disp('No file of this kind found...')
    end
end

%Concatonate with path
if ~batchflag
    if ~isempty(strfind(search,'/')), file=[search(1:max(strfind(search,'/'))),file];end
end

end