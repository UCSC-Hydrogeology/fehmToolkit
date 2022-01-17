function heatmapPoly(coor,z_in,clims)

%Create a 2-D heat map of data within polygon of interest
%SYNTAX
%   heatmap(coor,z_in) plots the values in the Nx1 vector 'z_in' at the
%   locations in the Nx2 matrix 'coor' as a heatmap.
%
%   heatmap(coor,z_in,clims) uses the 1x2 vector 'clims' [cmin, cmax] as
%   color limits.
%
%EXAMPLE
%   heatmap([1,1;3,2;3,1;2,2],[1;3;4;5]);
%   heatmap([1,1;3,2;3,1;2,2],[1;3;4;5],[3,5]);
%
%   See also IMAGESC, CONTOUR.
%
%   Written by Adam N. Price, UCSC Hydrogeology
%   Revision: 0.0 , 2019/07/25
disp('Constructing polygon, generating plot...')
f = scatteredInterpolant(coor(:,1),coor(:,2),z_in,'nearest');
x=min(coor(:,1)):range(coor(:,1))/1000:max(coor(:,1));
y=min(coor(:,2)):range(coor(:,2))/1000:max(coor(:,2));
[x,y]=meshgrid(x,y);
z=f(x,y);


xlims=[min(coor(:,1)),max(coor(:,1))];
ylims=[min(coor(:,2)),max(coor(:,2))];

%%% Make polygon
x_poly = coor(:,1);
y_poly = coor(:,2);

inside = boundary(x_poly,y_poly);



if exist('clims','var')
    imagesc(xlims,ylims,z,clims);
    hold on
else
    imagesc(xlims,ylims,z);
    hold on
end
% Plot polygon
plot(x_poly(inside),y_poly(inside),'black','LineWidth',3);

colormap('Hot');
colorbar;
xlabel('x');ylabel('y');

end