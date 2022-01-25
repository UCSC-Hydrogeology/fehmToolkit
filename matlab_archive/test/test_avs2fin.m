% test avs2fin

%% avs2fin jdf2d_p12
test_against_fixture('jdf2d_p12', 'p12', 'avs2fin_fixture.fin');


function test_against_fixture(fixture_name, run_name, output_fixture_filename)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_avs2fin__', fixture_name));

    if isfolder(test_dir)
        rmdir(test_dir, 's');
    end

    try
        mkdir(test_dir);
        cd(test_dir);
        
        copyfile(fullfile(fixture_dir, strcat(run_name, '.ini')), '.');
        copyfile(fullfile(fixture_dir, '*_sca_node.avs'), '.');

        avs2fin('test.fin');

        assert_files_match('test.fin', fullfile(fixture_dir, output_fixture_filename));
    catch e
        cd(initial_dir);
        rethrow(e);
    end

    rmdir(test_dir, 's');
    cd(initial_dir);
end
