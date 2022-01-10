function [rho_interp, visc_interp] = getwpi (wpi_in)

%Calculate density and viscosity interpolants from .wpi file.
%SYNTAX
%   rho_interp = getwpi(wpi_in) reads property data from wpi file,
%   returning an interpolant of fluid density.
%
%   [rho_interp,visc_interp] = getwpi(wpi_in) also returns a viscosity
%   interpolant.
%
%EXAMPLE
%   [rho_interp, visc_interp] = getwpi('grid_3.wpi');
%
%   See also ROCKPROP, GETPT.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2014/02/12

if nargin<1
disp('Locating water properties (.wpi) file...')
wpi_in=getfile('*.wpi');
end

%Read .wpi
disp(['Reading file: ',wpi_in])
fid=fopen(wpi_in);
lookup=textscan(fid,'%f%f %f%*f%*f %*f%*f%*f %f%*f%*f');
fclose(fid);

lookup_P=lookup{1};
lookup_T=lookup{2};
lookup_rho=lookup{3};
lookup_visc=lookup{4};

%Make density interpolant from lookup table
rho_interp=TriScatteredInterp(lookup_P,lookup_T,lookup_rho);
visc_interp=TriScatteredInterp(lookup_P,lookup_T,lookup_visc);

end

