function prop=getprop(propfile_in)

%Read property data from .cond, .perm, .ppor, or .rock file.
%SYNTAX
%   prop = getprop(propfile_in) reads property data from file, returning an
%   Nx3 matrix in most cases, or an Nx1 matrix for .ppor files, where N is
%   the number of nodes in the grid.
%
%EXAMPLE
%   permeability = getprop('grid_3.perm');
%   ppor = getprop('grid/grid_16.ppor');
%
%   See also ROCKPROP, GETPT.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0.1 , 2014/02/25
%
%   Updated 8/3/17 to remove line 36 for functionality with well macro
%   Tess Weathers
%   lines 27 and 29 updated to ignore header for well node specs

%Read file, with different format for .ppor files
disp(['Reading file: ',propfile_in])

fid=fopen(propfile_in);
if strcmp(propfile_in(end-4:end),'.ppor')
    prop_in=cell2mat(textscan(fid,'%f%f%*f%f','HeaderLines',2));
else
    prop_in=cell2mat(textscan(fid,'%f%f%*f%f%f%f','HeaderLines',1));
end
fclose(fid);

%Convert short format from file into long form, with one row per node
ind1=prop_in(:,1);
ind2=prop_in(:,2);
prop_in=prop_in(:,3:size(prop_in,2));

prop=zeros(ind2(end),size(prop_in,2));
for i=1:length(prop_in)
    prop(ind1(i):ind2(i),:)=repmat(prop_in(i,:),1+max([ind1(i),ind2(i)])-min([ind1(i),ind2(i)]),1);
end


end