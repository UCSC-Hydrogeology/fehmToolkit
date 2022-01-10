function dist=nodedist(node1,node2,fehmfile)

%Calculate the distances between two vectors of nodes.
%
%SYNTAX
%   dist = nodedist(node1, node2, fehmfile) calculates the shortest
%   possible distance between each pair of nodes, whose coordinates are
%   specified in 'fehmfile'.
%
%EXAMPLE
%   dist = nodedist([1, 30, 304], [6, 31, 318], 'p12.fehm');
%
%   See also GETNODE, GETNODEBELOW, NODE2COOR.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/09/24

%Read .fehm(n)
fprintf('%s\t%s\n','Reading file: ',fehmfile)
[~,coor]=getnode(fehmfile);

coor1=coor(node1,:);
coor2=coor(node2,:);

%Calculate distances

if ~isequal(size(coor1),size(coor2))
    error('node1 and node2 must be the same size.')
else
    dist=zeros(size(coor1,1),1)-1;
    for i=1:size(coor1,1)
        dist(i)=pdist([coor1(i,:);coor2(i,:)]);
    end
end
end