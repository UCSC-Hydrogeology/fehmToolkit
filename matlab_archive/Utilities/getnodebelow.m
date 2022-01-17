function node_out=getnodebelow(node_in,fehm_in,allnodes)

%Find nodes directly below another set of nodes in .fehm(n) file.
%SYNTAX
%   node_out = getnodebelow(node_in,fehm_in) returns a 1xN vector of node
%   numbers for the first node directly below those in the length-N vector
%   'node_in', per the coordinates provided in .fehm(n) file 'fehm_in'.
%
%   node_out = getnodebelow(node_in,fehm_in,allnodes) returns a 1xN cell
%   vector, each containing a Mx1 vector of all nodes below each member of
%   the length-N vector 'node_in'.
%
%EXAMPLE
%   node_out = getnodebelow([100;103;108],'grid_3.fehm');
%   node_out = getnodebelow(1007,'grid_3.fehm');
%   node_out = getnodebelow([3;7;107],'grid_3.fehm',1);
%
%   See also GETNODE.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/18

if nargin<3, allnodes=0;end

fprintf('%s\n','------------','GETNODEBELOW','------------')

n=length(node_in);

%Input node lists
disp(['Reading file: ',fehm_in])
[node,coor]=getnode(fehm_in);
coor=round(1000.*coor)./1000;

%Sort nodes by coordinate
disp('Sorting nodes by coordinate...')
[~,iz]=sort(coor(:,3),'descend');
coor=coor(iz,:);

[~,iy]=sort(coor(:,2));
coor=coor(iy,:);

[~,ix]=sort(coor(:,1));
coor=coor(ix,:);

node=node(iz);
node=node(iy);
node=node(ix);

disp('Identifying start points of columns...')
%Identify startpoints of columns in sorted set
[~,ia,~]=unique(coor(:,1:2),'rows','last');

disp('Locating nodes of interest in sorted set...')
%Locate nodes of interest (node_in) in sorted set
[~,~,in]=intersect(node_in,node,'stable');

fprintf('%s\n','Organizing nodes for output...')
if ~allnodes
    %Build array of nextnodes, with NaNs where no next node exists
    nextnode=circshift(node,-1);
    nextnode(ia)=NaN;
    
    node_out=nextnode(in);
    
else
    %Parse columns into cell-array
    node_out=cell(n,1);
    
    for i=1:n
        node_out{i}=node(in(i):ia(find(ia>in(i),1,'first')));
        if isempty(node_out{i}),node_out{i}=NaN;end
    end
end

fprintf('%s\n','-------------','/GETNODEBELOW','-------------')
end