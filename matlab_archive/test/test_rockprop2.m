% test rockprop2

%% Rockprop jdf3d_deep_p11ani
test_against_fixture('jdf3d_deep_p11ani', 'p11d600efto_GBv10BBv10_g981');


function test_against_fixture(fixture_name, run_name)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);
    test_dir = fullfile(tempdir, strcat('test_rockprop__', fixture_name));

    input_extensions = {'.fehm', '.zone', '.rpi'};
    % Note this only tests perm anisotropy (.cond, .ppor, .rock are checked
    % in the main rockprop tests).
    output_extensions = {'.perm'};

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

        rockprop2();

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
