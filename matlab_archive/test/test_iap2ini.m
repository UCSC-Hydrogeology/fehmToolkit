% test iap2ini

%% iap2ini np2d_cond
test_against_fixture('np2d_cond', 'iap2ini_fixture.ini');


%% iap2ini jdf2d_p12
test_against_fixture('jdf2d_p12', 'iap2ini_fixture.ini');


function test_against_fixture(fixture_name, output_fixture_filename)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_iap2ini__', fixture_name));

    if isfolder(test_dir)
        rmdir(test_dir, 's');
    end

    try
        mkdir(test_dir);
        cd(test_dir);

        iap2ini('test.ini', fixture_dir);

        assert_files_match('test.ini', fullfile(fixture_dir, output_fixture_filename));
    catch e
        cd(initial_dir);
        rethrow(e);
    end

    rmdir(test_dir, 's');
    cd(initial_dir);
end
