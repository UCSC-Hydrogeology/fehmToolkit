% test mkdotfiles3


%% mkdotfiles3 np3d_cond
test_against_fixture('np3d_cond', 'run', 1);


function test_against_fixture(fixture_name, run_name, restart_flag)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_mkdotfiles3__', fixture_name));

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

        mkdotfiles3(run_name, strcat(run_name, '.files'), restart_flag);

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
