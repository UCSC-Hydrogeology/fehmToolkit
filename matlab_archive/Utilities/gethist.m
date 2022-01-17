function his = gethist (histfile_in,sample_rate,nodes)

%Read nodal data and timing information from .hist file.
%SYNTAX
%   his = gethist(histfile_in) reads data from .hist file, returning a
%   data structure (his) containing time step information, node numbers,
%   and node coordinates.
%
%   his = gethist(histfile_in,sample_rate) also returns nodal data from
%   .hist file. A sample_rate of 1 returns all timesteps, with higher
%   integers downsampling the data.
%
%   his = gethist(histfile_in,sample_rate,nodes) only returns nodal data at
%   the specified node numbers.
%
%
%EXAMPLE
%   history_out = gethist('grid_2.hist');
%       returns only time step information
%
%   history_out = gethist('120_5perm2.hist',10,nodes);
%       returns time step and nodal data for every tenth timestep, at the
%       specified nodes.
%
%   See also GETFIN, GETINI, GETPROP, GETAVS.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2014/02/03

if nargin<2,sample_rate=1;end

if nargin<1
    disp('Locating .hist file...')
    histfile_in=getfile('*.hist');
end

%INPUT
fprintf('%s%s\n','Reading file: ',histfile_in)
hist_in=fileread(histfile_in);

[n,loc]=textscan(hist_in,'%f',1,'Headerlines',2);
hist_in(1:loc+1)=[];
n=cell2mat(n);

%node numbers
[nodecoor,loc]=textscan(hist_in,'%f%f%f%f',n);
hist_in(1:loc+1)=[];
nodecoor=cell2mat(nodecoor);

if nargin<3,nodes=nodecoor(:,1);end

[~,nodeorder,~]=intersect(nodecoor(:,1),nodes,'stable');
his.node=nodecoor(nodeorder,1);
his.coor=nodecoor(nodeorder,2:4);

%header info
spaces=regexp(hist_in,'\n');

i=1;
line=hist_in(spaces(i)+1:spaces(i+1)-1);
his.header='';
while isnan(str2double(line))
    i=i+1;
    his.header=[his.header,' ',line];
    line=hist_in(spaces(i)+1:spaces(i+1)-1);
end
hist_in(1:spaces(i))=[];
spaces(1:i)=[];

title=his.header;
openparen=strfind(title,'(');
closeparen=strfind(title,')');
ntitle=length(closeparen);

title=strrep(title,'(',',');
title=strrep(title,' ','_');

rmind=1:5;%removing 'node'
for i=1:length(closeparen),rmind=[rmind,openparen(i)+1:closeparen(i)];end
title(rmind)=[];
title=textscan(title,'_%s',ntitle,'Delimiter',',');
title=title{:};

%timestep information
disp('Parsing .hist data...')

%build format strings
skipline=['%*f',repmat('%*f',1,ntitle)];
skipstep=repmat({skipline},n,1);
skipstep=['%*f\n',sprintf('%s\n',skipstep{:})];

readline=['%*f',repmat('%f',1,ntitle)];
readstep=repmat({skipline},n,1);
readstep(nodeorder)={readline};
readstep=['%f\n',sprintf('%s\n',readstep{:})];

%read nodal data
readstring=[readstep,repmat(skipstep,1,sample_rate-1)];
nread=floor(length(spaces)/(n+1)/sample_rate);

parsed=textscan(hist_in,readstring,nread);
clearvars readstring

his.time=parsed{1};
if his.time(end)<0
    his.time(end)=[];
    timeflag=1;
else
    timeflag=0;
end

his.deltime=diff(his.time);

if numel(parsed)>1
    parsed=reshape(parsed(2:end),ntitle,length(nodeorder))';

    disp('Building structures...')
    for i=1:ntitle
        for j=1:length(nodeorder)
            eval(['his.',title{i},'(:,j)=parsed{j,i}(1:end-timeflag);']);
        end
    end
end

end