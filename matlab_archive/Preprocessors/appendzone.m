function appendzone(zone_append,outfile,sourcedir)

%Append a zone to an existing .zone file.
%SYNTAX
%   appendzone(ZONE TITLE/NUMBER) appends the zone designated by
%   'zone_append' from an _outside.zone file in the current directory to a
%   .zone file in the current directory. The original .zone file is backed
%   up as FILENAME_bak.
%
%       'zone_title' is either a numeric zone number, or a string
%       containing a title appearing before a zone in the corresponding
%       file (e.g. 'top', or 'left_w'). Strings of zone numbers will not
%       work correctly unless they exactly match that found in the file
%       (e.g. '00003'), numeric data types are preferred for this.
%
%   appendzone(VECTOR LIST OF NODES) appends the specified list of nodes
%   instead. This mode is used automatically when 'zone_append' has length
%   >1 and is of the NUMERIC type.
%
%   appendzone(zone_title,outfile) saves the combined .zone file to
%   'outfile' instead of overwriting the source .zone file. If the source
%   .zone file is not overwritten, no backup is created.
%
%   appendzone(zone_title,outfile,sourcedir) looks in 'sourcedir' for the
%   _outside.zone and .zone source files.
%
%EXAMPLE
%   appendzone('top')
%   appendzone(5,'appended.zone')
%   appendzone([5:10:1000], 'appended.zone')
%   appendzone('left_w','Test/Output/appended.zone','Test/Input')
%
%   See also GETZONE, MKFEHMDIR.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2015/01/20

%INPUT
%--------------------
if length(zone_append)>1 && isnumeric(zone_append)
    nodelist_flag=true;
else
    nodelist_flag=false;
end

if nargin<3, sourcedir='.';end
if ~strcmp(sourcedir(end),'/'),sourcedir=[sourcedir,'/'];end

disp('Locating zone (.zone) file...')
zonefile=getfile([sourcedir,'*.zone'],1);

if nargin<2, outfile=zonefile;end

%Prepare new zone
if ~nodelist_flag %Read file only if not appending explicit nodes
    disp('Locating outside zone (_outside.zone) file...')
    outsidefile=getfile([sourcedir,'*_outside.zone']);
    
    disp(['Reading file: ', outsidefile])
    newzone=getzone(zone_append,outsidefile);
else newzone=zone_append;
end

%Read .zone file
disp(['Reading file: ', zonefile])
fid=fopen(zonefile);
lines={fgetl(fid)};
while ischar(lines{end})
    lines(end+1)={fgetl(fid)};
end
fclose(fid);

%OUTPUT
%--------------------
%Make backup if necessary
if ~isempty(dir(outfile))
    disp(['Backing up ''',outfile,''' to: ',outfile,'_bak'])
    copyfile(outfile,[outfile,'_bak']);
end

%Write output
disp(['Writing output to: ',outfile])
zonenumber=sprintf('%05s',num2str(length(find(strcmp('nnum',lines)))+1));
n_nodes=['   ',num2str(length(newzone))];

fid=fopen(outfile,'w');
fprintf(fid,'%s\n',lines{1:end-3});
fprintf(fid,'%s\n%s\n%s',zonenumber,'nnum',n_nodes);
fprintf(fid,['\n%10i',repmat('%11i',1,9)],newzone);
fprintf(fid,'\n%s',lines{end-2:end-1});
fclose(fid);

end