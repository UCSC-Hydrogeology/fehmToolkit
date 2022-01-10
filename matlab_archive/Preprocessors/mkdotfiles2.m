function mkdotfiles2 (root, files_out, restartflag)

%Create a FEHM formatted .files file for either a new or restart run.
%SYNTAX
%   mkdotfiles(root) creates an FEHM formatted .files file using 'root'.EXT
%   as the filename for each entry. Assumes this is a new run, omitting an
%   entry for an .ini file. Output is saved as 'root'.files.
%
%   mkdotfiles(root,files_out) output is instead saved to 'files_out'.
%
%   mkdotfiles(root,files_out,restartflag) includes an entry for an .ini
%   file when 'restartflag' is non-zero.
%
%EXAMPLE
%   mkdotfiles('z_600_perm_12')
%   mkdotfiles('run_18','../run_18/R18.files',0)
%
%   See also MKFEHMDIR.
%
%   Written by Dustin Winslow, UCSC Hydrogeology
%   Revision: 1.0 , 2013/07/21
%   Revision: 2.0, 2018/06/25 by Tess Weathers to include output generated
%   by trac

if nargin<3, restartflag=0;end
if nargin<2, files_out=[root,'.files'];end

%MAKE CONTENT
%--------------------

strings={...
    ['root: ',root],...
    ['input: ',root,'.dat'],...
    ['outpu: ',root,'.out'],...
    ['grida: ',root,'.fehm'],...
    ['storo: ',root,'.stor'],...
    ['rsti: ',root,'.ini'],...
    ['rsto: ',root,'.fin'],...
    ['error: ','fehmn','.err'],...
    ['check: ',root,'.chk'],...
    ['zone: ',root,'.zone'],...
    ['look: ',root,'.wpi'],...
    ['hist: ',root,'.hist'],...
    ['trac: ',root,'.trc'],...
    [],...
    'all'};

if ~restartflag,strings(6)=[];end

%OUTPUT
%--------------------

%Write output 
disp(['Writing output to: ',files_out])

fid=fopen(files_out,'w');
fprintf(fid,'%s\n',strings{1:end-1});
fprintf(fid,'%s',strings{end});
fclose(fid);

end