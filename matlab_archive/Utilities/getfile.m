function file = getfile (search,zonefileflag,batchflag,lastflag)

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
%   file = getfile(..., lastflag) returns the last filename in the list
%   without asking the user.
%
%EXAMPLES
%   file = getfile('*.fehm*');
%   file = getfile('Gridfolder/Grid2/*.zone',1);
%   file = getfile('*sca_node*',0,1);
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2014/03/11

if nargin<2, zonefileflag=0;end
if nargin<3, batchflag=0;end
if nargin<4, lastflag=0;end

%Generate list of files in folder
filelist=dir(search);
filelist={filelist.name}';

if zonefileflag,
    rm=[];
    for i=1:length(filelist)
        if ~isempty(strfind(filelist{i},'_outside.zone')) || ~isempty(strfind(filelist{i},'_material.zone'))
            rm=[rm,i];
        end
    end
    filelist(rm)=[];
end

if isempty(filelist)
    warning(['No files matching ''',search,''' exist in specified location.']);
    file=0;
    return
end

%Select file
if batchflag, file=filelist;
else
    if length(filelist)==1
        file=filelist{1};
    else
        if lastflag, file=filelist{end};
        else
            disp('Multiple files found, please specify:')
            for i=1:length(filelist), disp([num2str(i),': ',filelist{i}]),end
            while ~exist('file','var')
                select=str2double(input('#: ','s'));
                if (select>0&&select<=length(filelist)), file=filelist{select};end
            end
            disp(' ')
        end
    end
end

%Concatonate with path
if ~batchflag
    if ~isempty(strfind(search,'/')), file=[search(1:max(strfind(search,'/'))),file];end
end

end