function vecMean = meanvec (outFile)

%Read and average all _vec_node.avs files in the current folder.
%SYNTAX
%   vecMean = meanvec(vecIn, outFile) outputs values to outFile.
%
%EXAMPLE
%   vecMean = meanvec(v, 'vectest_vec_node.avs');
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2015/04/08

fileList = getfile('*_vec_node.avs',0,1);
n = length(fileList);

disp(['Reading ',num2str(n), ' files...'])

if n < 2
    error('Fewer than two files present in directory.')
end

if nargin < 1
    outFile = [fileList{end}(1:end-13), 'mean_vec_node.avs'];
end

vecMean = getavs(fileList{1}) ./ n;

for i = 2:n
    vecMean = vecMean + getavs(fileList{i}) ./ n;
end

if outFile
    vec2avs(vecMean,outFile);
end

end