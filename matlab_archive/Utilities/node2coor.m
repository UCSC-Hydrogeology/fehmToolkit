function coor=node2coor(node,fehm_in)

%Look up coordinates for specified nodes using .fehm(n) file.
%SYNTAX
%   coor = node2coor(node,fehm_in) returns an n x 3 matrix containing
%   coordinates for all values of 'node', using .fehm(n) file 'fehm_in'.
%
%EXAMPLE
%   coor = node2coor([1;2;3;6;7;607;305;29],'grid_3.fehm');
%
%   See also GETNODE, GETNODEBELOW, GETZONE, GETELEM.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/18

%Read in coordinates between min and max of node array

if nargin<2
    disp('Locating FEHM (.fehm) file...')
    fehm_in=getfile('*.fehm*');
end

fid=fopen(fehm_in);
coor_in=textscan(fid,'%f',4*((max(node)-min(node))+1),'Delimiter','\t','HeaderLines',min(node)+1);
fclose(fid);

coor_in=reshape(coor_in{1},4,[])';

%Only include coor values which are shared in node
[~,inode,icoor]=intersect(node, coor_in(:,1));
coor=coor_in(icoor,2:4);

%Resort coor values to match with initial node input
coor(inode,:)=coor;

end