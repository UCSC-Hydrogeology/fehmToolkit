% test fin2ini

%% fin2ini np2d_cond
test_against_fixture('np2d_cond', 'fin2ini_fixture_1.ini', 0);


%% fin2ini np2d_cond iap_outsidezone
test_against_fixture('np2d_cond', 'fin2ini_fixture_2.ini', 1);


%% fin2ini jdf2d_p12
test_against_fixture('jdf2d_p12', 'fin2ini_fixture_1.ini', 0);


%% fin2ini jdf2d_p12 iap_outsidezone
test_against_fixture('jdf2d_p12', 'fin2ini_fixture_2.ini', 1);


function test_against_fixture(fixture_name, output_fixture_filename, useiap_outsidezone)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_fin2ini__', fixture_name));

    if isfolder(test_dir)
        rmdir(test_dir, 's');
    end

    try
        mkdir(test_dir);
        cd(test_dir);

        fin2ini('test.ini', fixture_dir, useiap_outsidezone);

        assert_files_match('test.ini', fullfile(fixture_dir, output_fixture_filename));
    catch e
        cd(initial_dir);
        rethrow(e);
    end

    rmdir(test_dir, 's');
    cd(initial_dir);
end
