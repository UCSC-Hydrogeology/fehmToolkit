function heatin(hfi_in)

%Calculates and writes heat input at base of model (.hflx file) using
%parameters from .hfi file.
%SYNTAX
%   heatin() reads a local '.hfi' file FILENAME.hfi and uses functions
%   within to calculate the total heat input (MW) for each bottom node from
%   a local '_outside.zone' file. Writes output to '.hflx' file
%   FILENAME.hflx. Reads back and plots '.hflx' output for verification.
%
%   heatin(hfi_in) instead reads 'hfi_in' as the input '.hfi' file. Output
%   will use the same root as 'hfi_in', with the '.hflx' extension.
%
%FORMAT
%   Heatflux input files (.hfi) use MATLAB syntax, and may use any number
%   of commented lines as a header. heatin() will execute any lines
%   verbatim that are found between the 'hflx' and 'stop' flags.
%
%   This block must contain a final function named "HFLX", but may contain
%   any number of subfunctions. HFLX must at least be a function of x, y,
%   and z, even if some or all of these dependencies are null.
%
%   Use ALL CAPS for all variable or function definitions, to avoid
%   confusion with the main program.
%
%EXAMPLE
%   heatin();
%   heatin('NewRun.hfi');
%
%   See also IPRES, ROCKPROP, HEATOUT.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/21

%INPUT
%----------------------

disp('Locating outsize zone (_outside.zone) file...')
outsidefile=getfile('*_outside.zone');

disp('Locating FEHM (.fehm) file...')
fehmfile=getfile('*.fehm*');

if nargin<1
    disp('Locating heatflux in (.hfi) file...')
    hfifile=getfile('*.hfi');
else
    hfifile=hfi_in;
end

disp('Locating area (.area) file...')
areafile=getfile('*.area');

%Generate bottom node list & area table
disp(['Reading file: ',outsidefile])
node=getzone('bottom',outsidefile);

disp(['Reading file: ',areafile])
area=getzone('bottom',areafile);

%Determine node coordinates
disp(['Reading file: ',fehmfile])
coor=node2coor(node,fehmfile);

%Read age and q functions from .hfi file
disp(['Reading file: ',hfifile])
fid=fopen(hfifile);
hfi=textscan(fid,'%s','Delimiter','\n');
fclose(fid);
hfi=hfi{1};

%CALCULATION
%-------------------------
%Define functions from .hfi file
start_ind=find(strcmp('hflx',hfi),1,'first')+1;
end_ind=find(strcmp('stop',hfi),1,'first')-1;

for i=start_ind:end_ind, eval([hfi{i}]);end

%Calculate heatflow for each node
fprintf('%s\n','Calculating heatflow using:',outsidefile,areafile,fehmfile,hfifile)
q=-abs(area(:,3).*HFLX(coor(:,1),coor(:,2),coor(:,3)));

disp(['Total heat input (MW): ',num2str(sum(q))])


%OUTPUT
%-------------------------

%Format arrays for output
[node,order]=sort(node);
q=q(order);
area=area(order,:);
coor=coor(order,:);

%Build output
root=outsidefile(1:end-13);
fprintf('\n%s\t%s\n','Writing file: ',[root,'.hflx'])
fid=fopen([root,'.hflx'],'w');
fprintf(fid,'%s\n','hflx');

newline=1;
for i=1:length(node)
    if newline,%set lower and upper node bounds for output
        lower=node(i);
        upper=lower;
        qout=q(i);
        newline=0;
    end
    
    if i==length(node)%if last node, automatically end line
        newline=1;
    else
        if (node(i)+1==node(i+1) && q(i+1)==qout), upper=upper+1;
        else newline=1;end
    end
    
    if newline, fprintf(fid,'%u\t%u\t%u\t%7.5E\t%s\n',lower,upper,1,qout,'0.');end
end
fprintf(fid,'%u\n',0);

fclose(fid);

%READBACK
%-----------------------------

%Create contour plot for visual check
fid=fopen([root,'.hflx']);
hflx_in=textscan(fid,'%f','Headerlines',1);hflx_in=hflx_in{1};
fclose(fid);

hflx_in=reshape(hflx_in(1:end-1),5,[])';
node=[];
hflx_plot=[];
for i=1:size(hflx_in,1)
    node=[node;(hflx_in(i,1):hflx_in(i,2))'];
    hflx_plot=[hflx_plot;repmat(hflx_in(i,4),1+hflx_in(i,2)-hflx_in(i,1),1)];
end
f=TriScatteredInterp(coor(:,1),coor(:,2),abs(hflx_plot./area(:,3)));%replace q with hflx to test read-in data
x=min(coor(:,1)):(max(coor(:,1))-min(coor(:,1)))/100:max(coor(:,1));
y=min(coor(:,2)):(max(coor(:,2))-min(coor(:,2)))/100:max(coor(:,2));
[x,y]=meshgrid(x,y);
z=f(x,y)*10.^6;%convert to Watts

xlims=[min(coor(:,1)),max(coor(:,1))];
ylims=[min(coor(:,2)),max(coor(:,2))];

imagesc(xlims,ylims,z);
colormap('Jet');
colorbar;
xlabel('x');ylabel('y');title('Heatflow (W/m^2)');

end