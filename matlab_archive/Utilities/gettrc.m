function [trc,header] = gettrc (trcfile_in)

%Read tracer information from .trc file.
%SYNTAX
%   trc = gettrc(trcfile_in) reads data from .trc file,
%   returning an NxM matrix, where N is the number of nodes in the
%   grid, and M is the number of data columns present.
%
%   [avs, header] = getavs(avsfile_in) also returns the header of the avs
%   file as a string.
%
%EXAMPLE
%   flow = getavs('grid_2.00015_vec_node.avs');
%
%   See also GETFIN, GETHFLX, GETPROP.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/19

if nargin<1
    disp('Locating .avs file...')
    trcfile_in=getfile('*.avs');
end

%Read sca_node
fprintf('%s\t%s\n','Reading file: ',trcfile_in)
fid=fopen(trcfile_in);
n=cell2mat(textscan(fid,'%f',1));
mvec=cell2mat(textscan(fid,'%f',n));
header=textscan(fid,'%s',n+1,'Delimiter','\n');
header=header{1};
header(1)=[];%remove white space after mvec line
trc=cell2mat(textscan(fid,['%*f',repmat('%f',1,sum(mvec))]));
fclose(fid);

%Format header output with column numbers
for i=1:length(mvec);
    startcol=sum(mvec(1:i));
    endcol=sum(mvec(1:i))+mvec(i)-1;
    if startcol==endcol
        colstring=[', Col ',num2str(startcol,'%u')];
    else
        colstring=[', Cols ',num2str(startcol,'%u'),':',num2str(endcol,'%u')];
    end
    
    header{i}=[header{i},colstring];
end

fprintf('%s\n','AVS Header:','-----------',header{:},'-----------')

end