function ipres(postflag)

%Calculates and writes initial hydrostatic pressure (.iap and .icp file)
%using parameters from .ipi file.
%SYNTAX
%   ipres() reads a local '.ipi' file and uses parameters
%   within to calculate the initial ambient hydrostat for nodes in a local
%   '.fehm' file using temperatures from a local '.fin' file. The initial
%   cold hydrostat is also calculated, assuming 2degC everywhere. Ambient
%   hydrostat is written to ROOT.iap, cold hydrostat is written to
%   ROOT.icp, with the same root name as the .fin file used.
%
%FORMAT
%   Initial pressure input files (.ipi):
%
%   BLANK_LINE
%   lagrit
%   DELTA_Z
%   REFERENCE_DEPTH, REFERENCE_PRESSURE, REFERENCE_TEMPERATURE
%   BLANK_LINE
%
%   Where lagrit is a literal string, and the first and fifth lines are
%   blank. DELTA_Z is the interval used in calculating hydrostatic
%   pressures, and the REFERENCE values serve as an anchor point, and all
%   calculated values are relative to this reference.
%
%EXAMPLE
%   ipres()
%
%   See also ROCKPROP, HEATIN, HEATOUT.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.1.1 , 2014/05/29
%   Revision: 1.1.2 , 180221 **AF**, fixed interpolation error

%INPUT
%--------------------------

if nargin<1,postflag=0;end

disp('Locating FEHM (.fehm) file...')
fehmfile=getfile('*.fehm*');

disp('Locating outsize zone (_outside.zone) file...')
outsidefile=getfile('*outside.zone');

disp('Locating FEHM output (.fin) file...')
finfile=getfile('*.fin');

disp('Locating water properties (.wpi) file...')
wpifile=getfile('*.wpi');

fprintf('%s\n\n','Locating ipres input (.ipi) file...')
ipifile=getfile('*.ipi');

root=finfile(1:end-4);

%Read .fehm(n)
disp(['Reading file: ',fehmfile])
[node,coor]=getnode(fehmfile);
coor=round(1e3.*coor)./1e3;%round to nearest mm for interpolation
nnode=length(node);

%Read _outside.zone
disp(['Reading file: ',outsidefile])
node_sflr=getzone('top',outsidefile);
coor_sflr=coor(node_sflr,:);

%Read .fin
disp(['Reading file: ',finfile])
fid=fopen(finfile);
T_in=cell2mat(textscan(fid,'%f','Headerlines',5));
fclose(fid);

%Read .ipi
disp(['Reading file: ',ipifile])
fid=fopen(ipifile);
ipi=cell2mat(textscan(fid,'%f','Delimiter',',','Headerlines',2));
fclose(fid);

%INTERPOLATION
%-------------------------
plane=0;
if length(unique(coor(:,1)))==1, plane=1;end
if length(unique(coor(:,2)))==1, plane=2;end

if plane%   WORKING IN 2D
    %Create false 3D by replicating grid into 3 parallel slices
    disp('Grid is 2D, replicating grid for false 3D...')
    coor_sflr_3d=repmat(coor_sflr,3,1);
    coor_sflr_3d(:,plane)=coor_sflr_3d(:,plane)+[10+zeros(length(node_sflr),1);zeros(length(node_sflr),1);-10+zeros(length(node_sflr),1)];
    coor_3d=repmat(coor,3,1);
    coor_3d(:,plane)=coor_3d(:,plane)+[10+zeros(length(node),1);zeros(length(node),1);-10+zeros(length(node),1)];
    T_3d=repmat(T_in,3,1);
else%       WORKING IN 3D
    coor_sflr_3d=coor_sflr;
    coor_3d=coor;
    T_3d=T_in;
end

rho_interp=getwpi(wpifile);

fprintf('\n%s\n','Generating seafloor interpolant...')
sflr_interp = TriScatteredInterp(coor_sflr_3d(:,1),coor_sflr_3d(:,2),coor_sflr_3d(:,3));

%INITIALIZE .IPI DATA
%--------------------------
%Set initial z,T,P point at top of grid
g=9.80665;
z_spc=ipi(1);
z0=max(coor_3d(:,3));
T0=ipi(4);
if z0==ipi(2)
    P0=ipi(3).*1e6;
else
    %Extrapolate up or down a column at bottom-water depth
    z_spc_tmp=sign(z0-ipi(2)).*min(abs(z0-ipi(2))/10,z_spc);
    delz=ipi(2):z_spc_tmp:z0; %#ok<BDSCI>
    delP=ipi(3).*1e6; %Convert MPa -> Pa
    for i=2:length(delz)
        delP(i)=delP(i-1)-g*z_spc_tmp*rho_interp(1e-6.*delP(i-1),T0);
    end
    P0=delP(end);
    %Note this process operates with different sign conventions than that
    %done below, as the bootstrapping direction is uncertain here.
end

%BUILD COLUMNS
%-------------
% **AF** Fixed problem with zvec assignment. 
%
xyvec=unique(coor_3d(:,1:2),'rows');%identify columns with unique (x,y)
%
% **AF** If we have highest point that is not
% even increment of z_spc, then zvec is too small and we get NaNs later
% from call to interp1. Add one more increment of z_spc to make sure that
% the array used for interpolation makes it to the seafloor!
%zvec=fliplr(0:z_spc:z0)';
zvec=fliplr(0:z_spc:(z0+z_spc))';
ncol=length(xyvec);

xmat=repmat(xyvec(:,1)',length(zvec),1);
ymat=repmat(xyvec(:,2)',length(zvec),1);
zmat=repmat(zvec,1,size(xyvec,1));

%DETERMINE T & P
%-------------------
disp('Generating temperature interpolant...')
T_interp = TriScatteredInterp(coor_3d(:,1),coor_3d(:,2),coor_3d(:,3),T_3d);

fprintf('\n%s\n%s\n','Determining temperatures...','(this can take a few minutes)')
Tmat=T_interp(xmat,ymat,zmat);

%Set values above seafloor to T0
sfvec=sflr_interp(xyvec(:,1),xyvec(:,2));
sfmat=repmat(sfvec',length(zvec),1);
Tmat(zmat>=sfmat)=T0;

Thalfmat=Tmat(1:end-1,:)+diff(Tmat,1,1)./2;

Tcoldmat=zeros(size(Thalfmat));
Tcoldmat(:)=min(T_3d);

if nnz(isnan(Tmat))>0
    warning('IPRES:NaNsDetected_Tmat','NaNs detected in Tmat: %i\n%s',nnz(isnan(Tmat)),'Check interpolants ranges.')
end

disp('Determining pressures...')
Pmat=zeros(size(Tmat));
Pmat(1,:)=P0;

Pcoldmat=zeros(size(Tmat));
Pcoldmat(1,:)=P0;

outind=ceil((.01:.01:1)'.*size(Pmat,1));
fprintf('%3u%s',0,'%')
for i=2:size(Pmat,1)
    ia=find(ismember(outind,i),1,'first');
    if ~isempty(ia),fprintf('\b\b\b\b%3u%s',ia,'%');end
    Pmat(i,:)=Pmat(i-1,:)+g.*z_spc.*rho_interp(1e-6.*Pmat(i-1,:),Thalfmat(i-1,:));
    Pcoldmat(i,:)=Pcoldmat(i-1,:)+g.*z_spc.*rho_interp(1e-6.*Pcoldmat(i-1,:),Tcoldmat(i-1,:));
end

%INTERPOLATE AND ASSIGN PRESSURES
fprintf('\n%s\n','Interpolating node pressures...')
zi=unique(coor_3d(:,3));

Pint=interp1(zvec,Pmat,zi);
Pint=Pint(:);

Pcoldint=interp1(zvec,Pcoldmat,zi);
Pcoldint=Pcoldint(:);

ximat=repmat(xyvec(:,1)',length(zi),1);
yimat=repmat(xyvec(:,2)',length(zi),1);
zimat=repmat(zi,1,size(xyvec,1));

coori=[ximat(:),yimat(:),zimat(:)];
[~,~,order]=intersect(coor_3d(1:nnode,:),coori,'rows','stable');
Pamb=1e-6.*Pint(order);
Pcold=1e-6.*Pcoldint(order);

if ~isempty(Pamb(isnan(Pamb)))
    warning ('IPRES:P_ambOutofRange','P_amb includes NaN values, lookup table may not cover full range of conditions.')
end

%OUTPUT
%-----------------------------
ext='.iap';
extc='.icp';
if postflag, ext(2)='f'; end
if postflag, extc(2)='f'; end

fprintf('\n%s\n',['Writing output to file: ',root,ext])
fid=fopen([root,ext],'w');
fprintf(fid,'%17.7f%21.7f%21.7f%21.7f',ones(4,1));
fprintf(fid,'\n%17.7f%21.7f%21.7f%21.7f',ones(length(Pamb)-4,1));
fprintf(fid,'\n%17.7f%21.7f%21.7f%21.7f',Pamb);
fclose(fid);

fprintf('%s\n',['Writing output to file: ',root,extc])
fid=fopen([root,extc],'w');
fprintf(fid,'%17.7f%21.7f%21.7f%21.7f',ones(4,1));
fprintf(fid,'\n%17.7f%21.7f%21.7f%21.7f',ones(length(Pcold)-4,1));
fprintf(fid,'\n%17.7f%21.7f%21.7f%21.7f',Pcold);
fclose(fid);

end