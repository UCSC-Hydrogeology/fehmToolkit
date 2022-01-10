function [node,coor] = getnode (fehm_in,limits)

%Read node and coordinate data from .fehm(n) file.
%SYNTAX
%   node = getnode(fehm_in) returns all node numbers in .fehm(n) file
%   'fehm_in'.
%
%   [node,coor] = getnode(fehm_in) also returns coordinates for all
%   returned nodes.
%
%   [...] = getnode(fehm_in,limits) returns only values for nodes with
%   coordinates inside the 3D block defined by 'limits', formatted as
%   [xmin,xmax,ymin,ymax,zmin,zmax].
%
%EXAMPLE
%   [node, coor] = getnode('grid_3.fehm');
%   node = getnode('grid_3.fehm',[3.9E3,4.1E3,7.9E3,8.1E3,400,800]);
%
%   See also GETNODEBELOW, NODE2COOR, GETZONE, GETELEM.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/18

if nargin<1
    disp('Locating FEHM (.fehm) file...')
    fehm_in=getfile('*.fehm*');
end

%Read in fehm file
fid=fopen(fehm_in);
n=textscan(fid,'%f',1,'Headerlines',1);
n=n{:};
mat=textscan(fid,'%f%f%f%f',n,'CollectOutput',1);
fclose(fid);
mat=mat{:};

node=mat(:,1);
coor=mat(:,2:4);

%Filter based on 'limits'
if nargin>1
    node=node(coor(:,1)>=limits(1) & coor(:,1)<=limits(2) & ...
        coor(:,2)>=limits(3) & coor(:,2)<=limits(4) & ...
        coor(:,3)>=limits(5) & coor(:,3)<=limits(6));
    coor=coor(node,:);
end

end