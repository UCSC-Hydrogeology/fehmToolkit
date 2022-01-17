function out=getzone2(zone_title,zone_in)

%Read one zone of node numbers or area data from _outside.zone, .zone, or
%.area files.
%SYNTAX
%   out = getzone(zone_title, zone_in) returns an Nx1 vector of node
%   numbers from a single zone in 'zone_in' files ending with _outside.zone
%   and .zone, or an Nx3 matrix of area data from 'zone_in' files ending
%   with .area, where N is the number of nodes within the specified zone.
%
%       'zone_title' is either a numeric zone number, or a string
%       containing a title appearing before a zone in the corresponding
%       file (e.g. 'top', or 'left_w'). Strings of zone numbers will not
%       work correctly unless they exactly match that found in the file,
%       numeric data types are preferred for this.
%
%EXAMPLE
%   zone6_nodes = getzone(6,'grid5.zone');
%   bottom_nodes = getzone('bottom','grid_outside.zone');
%   area_matrix = getzone('left_w','grid.area');
%
%   See also GETNODE, GETNODEBELOW, GETELEM.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/19
%   Revision: 1.01, 2013/02/26 by A. Fisher: flag and return on EOF

%Read input file
fid=fopen(zone_in);
strings=textscan(fid,'%s');
fclose(fid);
strings=strings{1};

%Convert numerical zone_titles to string with leading zeroes
if isnumeric(zone_title), zone_title=num2str(zone_title,'%1.5i'); end

%Locate zone_title section
%if isempty(find(strcmp(zone_title,strings),1)), error(['zone_title ','''',zone_title,''' not found in file.']),end
%
% if zone is not found, indicates reached end of file
if isempty(find(strcmp(zone_title,strings),1))
    zone_title=99999;
    out=-666;
    return
end
zone_title_ind=find(strcmp(zone_title,strings));

%Determine endpoints for specified section
nnum_ind=find(strcmp('nnum',strings));

nnum1_ind=nnum_ind(find(nnum_ind>zone_title_ind,1,'first'));

if nnum1_ind==nnum_ind(end),
    nnum2_ind=find(strcmp('stop',strings))+8;
else
    nnum2_ind=nnum_ind(find(nnum_ind==nnum1_ind)+1);
end

nnum=str2double(strings(nnum1_ind+1));

%Gather nodes for output, reshaping array in case of .area file
if nnum2_ind-nnum1_ind-nnum*3==10, area=1;else area=0;end
out=str2double(strings(nnum1_ind+2:nnum1_ind+1+(2*area+1)*nnum));
if area, out=reshape(out,length(out)/nnum,[])';end

end