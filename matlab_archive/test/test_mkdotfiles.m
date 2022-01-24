% test mkdotfiles

%% mkdotfiles np2d_cond
test_against_fixture('np2d_cond', 'cond', 0);


%% mkdotfiles np2d_p11
test_against_fixture('np2d_p11', 'run', 1);


%% mkdotfiles jdf3d_p12d_g981
test_against_fixture('jdf3d_p12d_g981', 'p12d_g981', 1);


%% mkdotfiles np3d_cond
test_against_fixture('np3d_cond', 'run', 1);


function test_against_fixture(fixture_name, run_name, restart_flag)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_mkdotfiles__', fixture_name));

    input_extensions = {};
    output_extensions = {'.files'};

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

        mkdotfiles(run_name, strcat(run_name, '.files'), restart_flag);

        for k=1:length(output_extensions)
            filename = strcat(run_name, output_extensions{k});
            assert_files_match(filename, fullfile(fixture_dir, filename));
        end
    catch e
        cd(initial_dir);
        rethrow(e);
    end

    rmdir(test_dir, 's');
    cd(initial_dir);
end
