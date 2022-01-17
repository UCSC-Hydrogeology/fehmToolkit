% test heatin

%% Heatin np2d_cond
test_against_fixture('np2d_cond', 'cond');


%% Heatin np2d_p11
test_against_fixture('np2d_p11', 'run');


%% Heatin jdf2d_p12
test_against_fixture('jdf2d_p12', 'p12');


%% Heatin jdf3d_p12d_g981
test_against_fixture('jdf3d_p12d_g981', 'p12d_g981');


%% Heatin jdf3d_p12
test_against_fixture('jdf3d_p12', 'p12');


%% Heatin jdf3d_conduit_p12
test_against_fixture('jdf3d_conduit_p12', 'p12');


%% Heatin np3d_cond
test_against_fixture('np3d_cond', 'run');


function test_against_fixture(fixture_name, run_name)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_heatin__', fixture_name));

    input_extensions = {'.fehm', '.zone', '.area', '.hfi'};
    output_extensions = {'.hflx'};

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

        heatin();

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