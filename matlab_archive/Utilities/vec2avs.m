function vec2avs (vecIn, outFile)

%Write M x 3 vector data as an avs file.
%SYNTAX
%   vec2avs(vecIn, outFile) outputs values to outFile.
%
%EXAMPLE
%   vec2avs(v, 'vectest_vec_node.avs');
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2015/04/08

vecIn = [(1:size(vecIn,1))', vecIn];

disp(['Writing vec to: ', outFile]);

fid = fopen(outFile,'w');

fprintf(fid, '%s\n%s\n', '1      3',...
    'Liquid Volume Flux (m3/[m2 s]), (m3/[m2 s])');

fprintf(fid, '%010u %16e %16e %16e\n', vecIn');

fclose(fid);

end