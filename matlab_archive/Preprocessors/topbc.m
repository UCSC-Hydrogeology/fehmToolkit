function topbc(T_top,ratio)

%Calculates the AIPED for the 'top' zone, for use in setting the top
%boundary condition with FEHM's flow macro. This is formatted and saved
%to ROOT.flow, where ROOT is based on the .STOR filename.
%SYNTAX
%   topbc() reads a local '_outside.zone' file, and '.stor' file, to
%   determine the volume of each node along the 'top' boundary. AIPED
%   values are then determined as AIPED=VOL.*RATIO (default ratio: 1e-8).
%   Also sets temperature of any incoming fluid along the top boundary to
%   T_top in degrees C (default T_top: 2). Values are written to file
%   ROOT.flow in a format appropriate for the FEHM FLOW macro.
%
%   topbc(T_top) specifies inflow temperature at the top boundary.
%
%   topbc(T_top,ratio) specifies the value to be used for RATIO.
%
%EXAMPLE
%   topbc();
%   topbc(1.8,1e-7);
%
%   See also IPRES, ROCKPROP, HEATIN, FIN2INI.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/10/09

if nargin<2
    ratio=1e-8;
    disp(['No input ratio, defaulting to: ',num2str(ratio)])
end

if nargin<1
    T_top=2;
    disp(['No input temperature, defaulting to: ',num2str(T_top),' degC'])
end

%INPUT
%----------------------

disp('Locating OUTSIDE ZONE (_outside.zone) file...')
outsidefile=getfile('*_outside.zone');

fprintf('%s\n\n','Locating STOR (.stor) file...')
storfile=getfile('*.stor');

%Generate top node list
disp(['Reading file: ',outsidefile])
topnode=getzone('top',outsidefile);

%Read nodal volume data
vol=getstor(storfile);
vol=vol(topnode);

%CALCULATION
%----------------------

aiped=abs(ratio.*vol);

%OUTPUT
%----------------------

%Format arrays for output
[topnode,order]=sort(topnode);
aiped=aiped(order);

%Build FLOW output
root=storfile(1:end-5);
fprintf('\n%s%s\n','Writing file: ',[root,'.flow'])
fid=fopen([root,'.flow'],'w');
fprintf(fid,'%s\n','flow');

newline=1;
for i=1:length(topnode)
    if newline,%set lower and upper node bounds for output
        lower=topnode(i);
        upper=lower;
        aipedout=aiped(i);
        newline=0;
    end
    
    if i==length(topnode)%if last node, automatically end line
        newline=1;
    else
        if (topnode(i)+1==topnode(i+1) && aiped(i+1)==aipedout), upper=upper+1;
        else newline=1;end
    end
    
    if newline, fprintf(fid,'%u\t %u\t %u\t %u\t %9.5f\t %7.5E\n',lower,upper,1,0,-T_top,aipedout);end
end
fprintf(fid,'%u\n',0);

fclose(fid);

end