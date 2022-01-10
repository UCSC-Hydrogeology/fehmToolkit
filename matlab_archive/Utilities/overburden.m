function ob=overburden(depth)

%Calculate sediment overburden with depth. For use with rockprop().
%
%SYNTAX
%   ob = overburden(depth) calculates overburden for vector of depths.
%   Function assumes the existance of RHOW, RHOG, GRAV, and SEDPOROSITY
%   global variables, which should be defined in an .rpi file.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/09/24

global RHOW RHOG GRAV SEDPOROSITY

if isempty('RHOW'),error('Variable RHOW not defined.'),end
if isempty('RHOG'),error('Variable RHOG not defined.'),end

rhowb=@(porosity)(1-porosity).*RHOG+porosity.*RHOW;

ob=zeros(length(depth),1);
for i=1:length(depth)
    ob(i)=sum((rhowb(SEDPOROSITY(0:depth(i)))-RHOW).*GRAV);
end

end