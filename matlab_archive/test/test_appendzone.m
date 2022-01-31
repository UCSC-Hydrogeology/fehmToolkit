% test appendzone

%% appendzone jdf3d_p12d_g981
test_against_fixture('jdf3d_p12d_g981', 'p12d_g981');


%% appendzone jdf3d_deep_p11ani
test_against_fixture('jdf3d_deep_p11ani', 'p11d600efto_GBv10BBv10_g981');


%% appendzone np2d_cond
test_against_fixture('np2d_cond', 'cond');


%% appendzone np2d_p11
test_against_fixture('np2d_p11', 'run');


%% appendzone np3d_cond
test_against_fixture('np3d_cond', 'run');


%% appendzone np3d_p11
test_against_fixture('np3d_p11', 'run');


function test_against_fixture(fixture_name, run_name)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_appendzone__', fixture_name));

    if isfolder(test_dir)
        rmdir(test_dir, 's');
    end

    try
        mkdir(test_dir);
        cd(test_dir);
        copyfile(fullfile(fixture_dir, strcat(run_name, '_outside.zone')), '.');
        copyfile(fullfile(fixture_dir, strcat(run_name, '_material.zone')), strcat(run_name, '.zone'));
        
        appendzone('top');
        appendzone('bottom', 'test.zone');

        assert_files_match('test.zone', fullfile(fixture_dir, strcat(run_name, '.zone')));
    catch e
        cd(initial_dir);
        rethrow(e);
    end

    rmdir(test_dir, 's');
    cd(initial_dir);
end
