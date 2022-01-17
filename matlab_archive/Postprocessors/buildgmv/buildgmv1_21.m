function buildgmv1_21(rootname)
%
%USE: buildgmv1_21('rootname')
%
%PURPOSE: To create a GMV input file (or a series of files) that can be
%used for visualization of FEHM output with either GMV or Paraview (or
%another tool that can work with GMV formatted files.
%
%PROCEDURE: 
%
%INPUT:
% This program requires a minimum of six files in the working directory:
% (1) fehm, (2) material.zone, (3) cond, (4) perm, (5) rock, (6) ppor. 
% For FEHM v3.x, these files have the following names by convention:
%      rootname.fehm, rootname_material.zone, rootname.cond, rootname.perm,
%      rootname.rock, rootname.ppor
%
%OUTPUT FILES:
% Initial version generates three files, as ParaView can read/display data
% from several files at once. A single file would be better for working 
% GMV, because it can only open one file, but this makes the program slow
% and reduces flexibility. This can be changed later.
% Blah, blah, blah
%
%EXAMPLE:
% buildgmv('p12_5_r2')
%
%   Written by Andrew Fisher, UCSC Hydrogeology
%   Revision: 0.99, 2014/03/20
%   Revision: 1.00, 2014/09/25, fixed bug with vector assignment
%   Revision: 1.1, 2015/02/06, fixed error in normalization of
%   three-dimensional vectors
%   Revision: 1.2, 2015/04/08, added material scalar data to the main GMV
%   file, so that we can edit display of scalar and vector data by material
%   type. 
%   Revision: 1.2.1, 2018/08/17, renamed call for utility subroutine
%   was getipres, now getiap (consistent with Winslow utility). Fixed bug
%   applied to 2D meshes, 3 coordinates for triangles, not 4 for
%   tetrahedra, code now sets coordination based on geometry.
%   Swapping Y and Z vectors for 2D - needed for FEHM AVS output.
%
% Check for existance of six essential files, get their names.
% Getfile returns an error if file does not exist
%
disp('Locating fehm (.fehm) file...')
fehmfile=getfile([rootname '*.fehm']);
disp('Locating material zone (.zone) file...')
zonefile=getfile([rootname '*material.zone']);
disp('Locating cond (.cond) file...')
condfile=getfile([rootname '*.cond']);
disp('Locating perm (.perm) file...')
permfile=getfile([rootname '*.perm']);
disp('Locating rock (.rock) file...')
rockfile=getfile([rootname '*.rock']);
disp('Locating ppor (.ppor file...')
pporfile=getfile([rootname '*.ppor']);
%
% Check for existance of optional files, get names if they exist
% Getfile2 returns 'nofile' if file does not exist 
% Also - this version requires at least two sets of sca and vec files, if
% there are any of these - otherwise there is a syntax problem with putting
% file names in a cell structure. Grrr. 
%
disp('Locating warm ambient pressure (.iap) file...')
iapfile=getfile2([rootname '*.iap']);
disp('Locating cold hydrostatic pressure (.icp) file...')
icpfile=getfile2([rootname '*.icp']);
disp('Locating scalar node (sca_node) file(s)...')
scafile=getfile2([rootname '*sca_node*'],0,1);
disp('Locating vector node (vec_node) file(s)...')
vecfile=getfile2([rootname '*vec_node*'],0,1);
%
% Read data from fehm file
%
fprintf('%s\t%s\n','Reading file: ',fehmfile)
[node,coor]=getnode(fehmfile);
[nnod,ncol]=size(node);
elem=getelem(fehmfile);
[nele,ncoe]=size(elem);
%
% Read data from material zone file
% Would be faster to have a utility that reads entire material.zone file,
% assigns materials as specified, rather than cycling one zone at a time...
%
fprintf('%s\t%s\n','Reading file: ',zonefile)
izone=1;
material=zeros(nnod,1);
%
%fprintf('%s\n','Skipping zone file for now to speed debugging. FIX ME LATER!')
while izone~=9999
    fprintf('%s\t%.0f\n','Reading data for zone: ',izone)
    nodz=getzone2(izone,zonefile);
    if nodz(1,1)~=-666;
       material(nodz(:),1)=izone;
       izone=izone+1;
    else
      izone=9999;
    end
end    
%
% Read property data from cond, perm, rock, and ppor files
%
fprintf('%s\t%s\n','Reading file: ',condfile)
cond=getprop(condfile);
fprintf('%s\t%s\n','Reading file: ',permfile)
perm=getprop(permfile);
fprintf('%s\t%s\n','Reading file: ',rockfile)
rock=getprop(rockfile);
fprintf('%s\t%s\n','Reading file: ',pporfile)
ppor=getprop(pporfile);
%
% Read from ipres output files if they exist (ambient warm hydrostat, cool
% hydrostat)
%
iapex=strcmp(iapfile,'nofile');
icpex=strcmp(icpfile,'nofile');
if iapex==0
    fprintf('%s\t%s\n','Reading file: ',iapfile)
%    ambpres=getipres(iapfile);
    ambpres=getiap(iapfile);
end
if icpex==0
    fprintf('%s\t%s\n','Reading file: ',icpfile)
%    colpres=getipres(icpfile);
    colpres=getiap(icpfile); 
end
%
% All single-file (pre-FEHM) data have been read. 
% Make a GMV file with mesh information: geometry and properties.
%
outfile1=strcat(rootname,'_mesh.gmv');
%
fprintf('%s\t%s\n','Writing mesh file: ',outfile1)
fid=fopen(outfile1,'w');    
fprintf(fid,'%s \n \n','gmvinput ascii');
%
% nodes
%
fprintf(fid,'%s %d \n',' nodes ',nnod);
fprintf('%s \n','Writing node coordinates...')
nrow=7;
formmat=repmat('%10.3f ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,coor(1:nnod,1));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,formmat,coor(1:nnod,2));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,formmat,coor(1:nnod,3));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% elements
%
fprintf(fid,'%s %d \n',' cells ',nele);
fprintf('%s \n','Writing elements...')
formele=repmat('%d ',1,ncoe);  % format for element information
formele=['%s ' formele '\n'];
geom=' tet ';
if ncoe==3
    geom=' tri ';
end
for ne=1:nele
%   fprintf(fid,'%s \n %s %d %d %d %d \n',' tet 4','   ',elem(ne,1:4));
   fprintf(fid,'%s %d \n',geom,ncoe);
   fprintf(fid,formele,'     ',elem(ne,1:ncoe));
end
fprintf(fid,'\n');
%
% variables (properties)
%
fprintf(fid,'%s \n','variable'); 
%
% materials
%
fprintf('%s \n','Writing materials...')
fprintf(fid,'%s \n','material 1');
nrow=20;
formmat=repmat('%d ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,material(1:nnod));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% permeability - X
%
fprintf('%s \n','Writing permeabilities...')
fprintf(fid,'\n%s\n','PermX 1');
nrow=5;
formmat=repmat('%e ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,perm(1:nnod,1));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% permeability - Y
%
fprintf(fid,'\n%s\n','PermY 1');
formmat=repmat('%e ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,perm(1:nnod,2));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% permeability - Z
%
fprintf(fid,'\n%s\n','PermZ 1');
formmat=repmat('%e ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,perm(1:nnod,3));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% thermal conductivity - X
%
fprintf('%s \n','Writing thermal conductivities...')
fprintf(fid,'\n%s\n','CondX 1');
nrow=8;
formmat=repmat('%6.3f ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,cond(1:nnod,1));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% thermal conductivity - Y
%
fprintf(fid,'\n%s\n','CondY 1');
formmat=repmat('%6.3f ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,cond(1:nnod,2));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% thermal conductivity - Z
%
fprintf(fid,'\n%s\n','CondZ 1');
formmat=repmat('%6.3f ',1,nrow);
formmat=[formmat ' \n'];
fprintf(fid,formmat,cond(1:nnod,3));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% density
%
fprintf('%s \n','Writing rock properties...')
fprintf(fid,'\n%s\n','Density 1');
nrow=5;
formmat=repmat('%e ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,rock(1:nnod,1));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');
%
% heat capacity
%
fprintf(fid,'\n%s\n','HeatCap 1');
formmat=repmat('%e ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,rock(1:nnod,2));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');%
%
% porosity
%
fprintf(fid,'\n%s\n','Porosity 1');
nrow=8;
formmat=repmat('%6.3f ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,rock(1:nnod,3));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');%
%
% compressibility
%
fprintf(fid,'\n%s\n','Compress 1');
nrow=5;
formmat=repmat('%e ',1,nrow);  
formmat=[formmat ' \n'];
fprintf(fid,formmat,ppor(1:nnod,1));
   if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
fprintf(fid,'\n');%
%
% ambient hydrostatic
%
fprintf('%s \n','Checking for cold/ambient properties...')
nrow=7;
if iapex==0
   fprintf(fid,'\n%s\n','AmbHyd 1');
   formmat=repmat('%7.4f ',1,nrow);  
   formmat=[formmat ' \n'];
   fprintf(fid,formmat,ambpres(1:nnod,1));
      if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
   fprintf(fid,'\n');%
end
%
% cold hydrostatic
%
if icpex==0
   fprintf(fid,'\n%s\n','CoolHyd 1');
   formmat=repmat('%7.4f ',1,nrow);  
   formmat=[formmat ' \n'];
   fprintf(fid,formmat,colpres(1:nnod,1));
      if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
   fprintf(fid,'\n');%
end
%
fprintf(fid,'%s \n','endvars');
fprintf(fid,'%s \n','endgmv');
fclose(fid);
fprintf('%s\t%s\n','Finished mesh file: ',outfile1)

% Look for scalar and vector data and prepare GMV files. Assumption is that
% there is an equal number of each, with corresponding file names, allowing
% scalar and vector data to be combined in a single file. We can add an
% option later to combine mesh, scalar and vector info in a single file,
% but this is not needed for paraview because that program can handle
% multiple input files for the same simulation/timestep. 
%
[nsca,col]=size(scafile);
for nf=1:nsca
   scafin=scafile{nf,1};
   vecfin=vecfile{nf,1};
   nodata=strcmp(scafin,'nofile');
   if nodata==1   % no FEHM output
      fprintf('%s \n','Done processing mesh data')
      return
   else           % yes FEHM output, build GMV file of positions and output 
%
% Build one GMV file for each pair of SCA and VEC files
%
      dotpos=findstr(scafin,'.');
      chars=scafin(dotpos+1:dotpos+5);
      outfehm=strcat(rootname,'_',chars,'_bg.gmv');
      avsnum=str2num(chars);
%
      fprintf('%s\t%s\n','Writing fehm output: ',outfehm)
      fid=fopen(outfehm,'w');    
      fprintf(fid,'%s \n \n','gmvinput ascii');
%
% nodes
%
      fprintf(fid,'%s %d \n',' nodes ',nnod);
      fprintf('%s \n','Writing node coordinates...')
      nrow=7;
      formmat=repmat('%10.3f ',1,nrow);  
      formmat=[formmat ' \n'];
      fprintf(fid,formmat,coor(1:nnod,1));
      if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
      fprintf(fid,formmat,coor(1:nnod,2));
      if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
      fprintf(fid,formmat,coor(1:nnod,3));
      if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
      fprintf(fid,'\n');
%
% elements
%
      fprintf(fid,'%s %d \n',' cells ',nele);
      fprintf('%s \n','Writing elements...')
      for ne=1:nele
%         fprintf(fid,'%s \n %s %d %d %d %d \n',' tet 4','   ',elem(ne,1:4));
      fprintf(fid,'%s %d \n',geom,ncoe);
      fprintf(fid,formele,'     ',elem(ne,1:ncoe));
end

      end
      fprintf(fid,'\n');%
%
% variables (scalar output first, then vector output)
%
      fprintf(fid,'%s \n','variable');
      [scaavs,scahead]=getavs(scafin);
      [nhead,foo]=size(scahead);
%
% AF 2015/04/08 - added material information to the scalar/vector buildgmv
% output file, so we can edit what is shown by material (not just but
% output from model.
% 
% materials
%
      fprintf('%s \n','Writing materials...')
      fprintf(fid,'%s \n','material 1');
      nrow=20;
      formmat=repmat('%d ',1,nrow);  
      formmat=[formmat ' \n'];
      fprintf(fid,formmat,material(1:nnod));
      if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
      fprintf(fid,'\n');
%
      for nh=1:nhead
         scaheader=scahead{nh,1};
         parpos=findstr(scaheader,'(');
         htrimsca=regexprep(scaheader(1:parpos-1),'[^\w'']','');
         fprintf(fid,' %s%s \n',htrimsca,' 1');
         nrow=5;
         formmat=repmat('%e ',1,nrow);  
         formmat=[formmat ' \n'];
         fprintf(fid,formmat,scaavs(1:nnod,nh));
         fprintf(fid,'\n');%
         if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
      end
      fprintf(fid,'%s \n \n',' endvars');
%
      if avsnum>1
         [vecavs,vechead]=getavs(vecfin);
%**AF reassign Y and Z vectors for 2D, bug in how FEHM outputs AVS vectors
         if ncoe == 3
            vecavs(:,3)=vecavs(:,2);
            vecavs(:,2)=0.;
         end
            
%
% Normalize flow vectors to create new vector variable
% ratio = scaling factor, gets 4.5 orders of magnitude on scale of 0-10
%         with a natural log ratio, using 4.54e-5 for now
% small = normalized vector to be set = 0, would be a dot anyhow.
% bigvec = value to be mapped to 10. In this version = vecmax, but could be
%          set to a fixed scale later if desired.
% vecfact = scaling factor for each vector
% vecnorm = normalized vector, scale of 0 to 10, such that:
%           bigvec = 10
%           bigvec/ratio = 0
%
         ratio=4.54e-5;
         small=0.01;
%
         vectot=sqrt(vecavs(:,1).*vecavs(:,1)+vecavs(:,2).*vecavs(:,2)+vecavs(:,3).*vecavs(:,3));
         vecmim=min(vectot);
         vecmax=max(vectot);
         bigvec=vecmax;
         vecfact=vectot/bigvec;
%
% Normalize vectors, zeroing out small ones. We could do a final step of
% zeroing normalized vectors as well.
%
         toosmall=vecfact<ratio;  %find values less than ratio
         subval=vecfact.*toosmall; 
         vecfact=vecfact-subval;  %zero small values
         zeroval=vecfact==0;      %locate zero values, vector array
         minval=zeroval*ratio;    %what zero values will be set to, vector array
         vecfact=vecfact+minval;  %all zero values set to ratio
         vecnorm=10+log(vecfact);
%
%         vnormx=vecnorm.*vecavs(:,1)./vectot; *these two lines were wrong
%         vnormy=vecnorm.*vecavs(:,2)./vectot; *for a 3D problem, see below
         vnormz=vecnorm.*vecavs(:,3)./vectot;
%
%  Additional calculations required for the other two vector components in
%  three dimensions.
%
         vnormxy=sqrt((vecnorm.^2)-(vnormz.^2));
         vnormx=vnormxy.*vecavs(:,1)./vectot;
         vnormy=vnormxy.*vecavs(:,2)./vectot;
%
%  For all total normalized vector lengths < small (now 0.01), set
%  all three components =0.0
%
         toosmall=abs(vecnorm)<small;
         vnormx=vnormx-(toosmall.*vnormx);
         vnormy=vnormy-(toosmall.*vnormy);
         vnormz=vnormz-(toosmall.*vnormz);
%
% Write normalized vector data
%
%         fprintf(fid,'%s \n',' vectors');
%         fprintf(fid,'%s \n',' NormFVel  1  3');
%      fprintf(fid,'%s \n ',' NormFVel  1  3  1');
%      fprintf(fid,'%s \n',' NormVelX  NormVelY  NormVelZ');
%         fprintf(fid,formmat,vnormx);
%         if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
%         fprintf(fid,formmat,vnormy);
%         if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
%         fprintf(fid,formmat,vnormz);
%         if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
%         fprintf(fid,'%s \n \n',' endvect');

      fprintf(fid,'%s \n',' velocity 1');
%      for nv=1:3
%         fprintf(fid,formmat,vecavs(1:nnod,nv));
%         if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
%      end
%
         fprintf(fid,formmat,vnormx);
         if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
         fprintf(fid,formmat,vnormy);
         if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
         fprintf(fid,formmat,vnormz);
         if rem(nnod,nrow)~=0, fprintf(fid,'\n'); end
      fprintf(fid,'\n');
   end
%
%
   fprintf(fid,'%s \n','endgmv');
   fclose(fid);
   fprintf('%s\t%s\n','Finished fehm file: ',outfehm)
%
%   save matfile with all variables, for debugging if desired
%      
   save('buildgv.mat')
      
end

end
