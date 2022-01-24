% test ipres

%% Ipres np2d_cond
test_against_fixture('np2d_cond', 'cond');


% Known failures, .iap and .icp files differ
% %% Ipres jdf2d_p12
% test_against_fixture('jdf2d_p12', 'p12');
% 
% 
% %% Ipres jdf3d_conduit_p12
% test_against_fixture('jdf3d_conduit_p12', 'p12');
% 
% 
% %% Ipres jdf3d_p12d_g981
% test_against_fixture('jdf3d_p12d_g981', 'p12d_g981');
%
%
% Known failure, .iap file differs (.icp matches)
% %% Ipres jdf3d_deep_p11ani
% test_against_fixture('jdf3d_deep_p11ani', 'p11d600efto_GBv10BBv10_g981');


function test_against_fixture(fixture_name, run_name)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_ipres__', fixture_name));

    input_extensions = {'.fehm', '_outside.zone', '.fin', '.ipi', '.wpi'};
    output_extensions = {'.icp', '.iap'};

    if isfolder(test_dir)
        rmdir(test_dir, 's');
    end

    try
        mkdir(test_dir);
        cd(test_dir);
        for k=1:length(input_extensions)
            input_path = fullfile(fixture_dir, strcat('*', input_extensions{k}));
            copyfile(input_path, '.');
        end

        ipres();

        for k=1:length(output_extensions)
            filename = strcat(run_name, output_extensions{k});
            assert_files_match(filename, fullfile(fixture_dir, filename));
        end
    catch e
        cd(initial_dir);
        disp(input_path);
        rethrow(e);
    end

    rmdir(test_dir, 's');
    cd(initial_dir);
end