% test modeltime

%% modeltime np2d_cond
test_against_fixture('np2d_cond', 'cond');


%% modeltime np3d_cond
test_against_fixture('np3d_cond', 'run');


function test_against_expected(fixture_name, expected_time, expected_deltime)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);

    [time,deltime]=modeltime(fixture_dir);
    assert(time == expected_time, '%f (actual) != %f (expected)', time, expected_time);
    assert(deltime == expected_deltime, '%f (actual) != %f (expected)', deltime, expected_deltime);
end
