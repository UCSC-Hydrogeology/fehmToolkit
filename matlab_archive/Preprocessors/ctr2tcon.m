function tc_by_depth=ctr2tcon(varargin)

%Calculate a monotonic thermal conductivity profile as a function of depth.
%SYNTAX
%   Must include one argument for each set of sediment nodes with a unique
%   vertical structure. Each argument should be a vector including each
%   sediment node depth, with the last entry being the total sediment
%   depth.
%
%   The last argument can be a function specifying the CTR by depth.
%
%   tc_by_depth = ctr2tcon(sediment_node_vector, CTR_fun) returns a TC
%   profile using the specified node depths and CTR function. Output is a
%   vector of TC values with 1-m spacing.
%   
%   tc_by_depth = ctr2tcon(sediment_node_vector) uses the default (Juan de
%   Fuca) CTR function.
%
%EXAMPLE
%   tc_by_depth = ctr2tcon([0,100,450], @(z)0.603.*z);
%   tc_by_depth = ctr2tcon([0,100],[0,50,100],[0,20,80,100],@(z)0.603.*z);
%
%   See also ROCKPROP.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1 , 2015/10/19

%DEFINITIONS
if isa(varargin{end},'function_handle')
    %Use input function for CTR
    ctrfun=varargin{end};
    varargin(end)=[];
else
    %Use JdF CTR function
    disp('No CTR function provided, assuming corrected JdF curve.')
    ctrfun=@(z)0.603.*z+0.000531.*z.^2-0.000000684.*z.^3;
end
n=length(varargin);
varargin=[varargin;cell(1,n)];
for i=1:n
    %Force row vectors
    if size(varargin{1,i},1)<size(varargin{1,i},2), varargin{1,i}=varargin{1,i}';end
    %Separate last entries in each column as seddepths
    varargin{2,i}=varargin{1,i}(end);
    varargin{1,i}(end)=[];
end

%Create by-column structures
cols=cell2struct(varargin,{'depth','seddepth'});

%Identify unique node depths
[depth,~,tci]=unique(abs(vertcat(cols.depth)));
depth=floor(depth);

%Set initial guesses for tc optimization
tc0=ones(max(tci),1);

for i=1:n
    %Generate interval breakpoints
    if length(cols(i).depth)>1
        interval=mean([cols(i).depth(2:end),cols(i).depth(1:end-1)],2);
    else
        interval=[];
    end
    cols(i).interval=[0;round(interval);ceil(cols(i).seddepth)];
    
    %Claim indices for TC values
    cols(i).tci=tci(1:length(cols(i).depth));
    tci(1:length(cols(i).depth))=[];
end

%Make total depth column
z_all=(0:max([cols.seddepth]))';
ctrref=ctrfun(z_all);

%OPTIMIZE
tc=fminsearch(@(tc) ctrerr(tc,ctrref,cols),tc0);
tc=round(1000.*tc)./1000;
[~,cols]=ctrerr(tc,ctrref,cols);

%TC DEPTH PROFILE
tc_by_depth=zeros(size(z_all));
tc_by_depth(1:depth(2))=tc(1);
for i=2:length(depth)-1
    tc_by_depth(depth(i)+1:depth(i+1))=tc(i);
end
tc_by_depth(depth(end):end)=tc(end);

%PLOTS
%Reference tcon
tconref=(ctrref-circshift(ctrref,1)).^-1;
tconref(1)=tconref(2);

markers=repmat('o+*xsd^v><',1,5);
legendtext=cell(n+1,1);

figure(1)
plot(ctrref,-z_all,'-k')
legendtext{1}='Reference';
hold on
for i=1:n
    plot(cols(i).ctr,-cols(i).interval(2:end),[markers(i),'k'])
    legendtext{i+1}=['Column ',num2str(i)];
end
hold off
xlabel('CTR [m^2 K/W]')
ylabel('Depth (mbsf)')
legend(legendtext{:});

figure(2)
for i=1:n
    maxind=ceil(cols(i).seddepth+1);
    subplot(ceil((n)./2),2,i)
    plot(tconref(1:maxind),-z_all(1:maxind),'-k',cols(i).tc,-z_all(1:maxind),'-r')
    xlim([1.3,1.7])
    ylabel('Depth (mbsf)')
    xlabel(['Column ',num2str(i),' TC [W/(m K)]'])
    legend('Reference','Computed')
end

end


function [err,cols]=ctrerr(tc,ctrref,cols)

tc=round(1000.*tc)./1000;

for i=1:length(cols)
    for j=1:length(cols(i).depth)
        %Assign TC values to specified intervals
        cols(i).tc(cols(i).interval(j)+1:cols(i).interval(j+1)+1,1)=tc(cols(i).tci(j));
        %Calculate CTR
        cols(i).ctr(j,1)=sum(1./cols(i).tc(1:cols(i).interval(j+1)+1));
    end
    
    %Calculate column error
    cols(i).err=cols(i).ctr-ctrref(cols(i).interval(2:end));
    cols(i).totalerr=mean(cols(i).err.^2);
end

%Calculate total error
err=sum([cols.totalerr]);

end