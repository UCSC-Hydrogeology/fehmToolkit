% test fin2ini2

%% fin2ini2 np2d_cond
test_against_fixture('np2d_cond', 'fin2ini2_fixture.ini');


%% fin2ini2 jdf2d_p12
test_against_fixture('jdf2d_p12', 'fin2ini2_fixture.ini');


function test_against_fixture(fixture_name, output_fixture_filename)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_fin2ini2__', fixture_name));

    if isfolder(test_dir)
        rmdir(test_dir, 's');
    end

    try
        mkdir(test_dir);
        cd(test_dir);

        fin2ini2('test.ini', fixture_dir);

        assert_files_match('test.ini', fullfile(fixture_dir, output_fixture_filename));
    catch e
        cd(initial_dir);
        rethrow(e);
    end

    rmdir(test_dir, 's');
    cd(initial_dir);
end
