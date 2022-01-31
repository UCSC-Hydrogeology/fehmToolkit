% test modeltime

%% modeltime np2d_cond
test_against_expected('np2d_cond', 36500000000, 18024418.611298);


%% modeltime np3d_cond
test_against_expected('np3d_cond', 5475000000, 1338452148.437500);


function test_against_expected(fixture_name, expected_time, expected_deltime)
    initial_dir = pwd;
    fixture_dir = fullfile(initial_dir, 'fixtures', fixture_name);

    [time,deltime]=modeltime(fixture_dir);
    assert(round(time, 6) == expected_time, '%f (actual) != %f (expected)', time, expected_time);
    assert(round(deltime, 6) == expected_deltime, '%f (actual) != %f (expected)', deltime, expected_deltime);
end
