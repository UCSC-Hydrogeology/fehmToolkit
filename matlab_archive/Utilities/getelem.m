function elem = getelem (fehm_in)

%Read element data from .fehm(n) file.
%SYNTAX
%   elem = getelem(fehm_in) retrieves element data from .fehm(n) file
%   'fehm_in'. Returns an Nx4 matrix of node numbers, where N is the number
%   of elements, and nodes on the same row are members of the same element.
%
%EXAMPLE
%   elem = getelem('grid_3.fehm');
%
%   See also GETNODE, GETZONE.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/18

%Read in fehm file
fid=fopen(fehm_in);
nnode=textscan(fid,'%f',1,'Headerlines',1);
nnode=nnode{:};

nelem=textscan(fid,'%f%f',1,'CollectOutput',1,'Headerlines',nnode+3);
nelem=nelem{:};

elem=textscan(fid,['%*f',repmat('%f',1,nelem(1))],nelem(2),'CollectOutput',1);
fclose(fid);
elem=elem{:};

end