% test datreset

%% datreset np2d_cond
test_against_fixture('np2d_cond', 'cond', 'datreset_fixture.dat');


%% datreset jdf3d_p12d_g981
test_against_fixture('jdf3d_p12d_g981', 'p12d_g981', 'datreset_fixture.dat');


function test_against_fixture(fixture_name, run_name, output_fixture_filename)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_datreset__', fixture_name));

    if isfolder(test_dir)
        rmdir(test_dir, 's');
    end

    try
        mkdir(test_dir);
        cd(test_dir);
        input_path = fullfile(fixture_dir, strcat(run_name, '.dat'));
        copyfile(input_path, 'test.dat');

        datreset(1234, 7300);

        assert_files_match('test.dat', fullfile(fixture_dir, output_fixture_filename));
    catch e
        cd(initial_dir);
        rethrow(e);
    end

    rmdir(test_dir, 's');
    cd(initial_dir);
end
