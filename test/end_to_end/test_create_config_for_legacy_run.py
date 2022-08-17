from fehm_toolkit.config import RunConfig
from fehm_toolkit.fehm_runs.create_config_for_legacy_run import create_config_for_legacy_run


def test_create_config_for_legacy_run_flat_box(tmp_path, end_to_end_fixture_dir):
    run_directory = end_to_end_fixture_dir / 'flat_box' / 'p12'

    fixture_file = run_directory / 'config.yaml'
    output_file = tmp_path / 'config.yaml'
    create_config_for_legacy_run(
        directory=run_directory,
        config_file=output_file,
        input_file=run_directory / 'p12.dat',  # specified to avoid other test fixtures in folder
        final_conditions_file=run_directory / 'p12.fin',  # specified to avoid other test fixtures in folder
        water_properties_file=run_directory / '../../nist120-1800.out',
    )
    assert RunConfig.from_yaml(output_file) == RunConfig.from_yaml(fixture_file)


def test_create_config_for_legacy_run_outcrop_2d(tmp_path, end_to_end_fixture_dir):
    run_directory = end_to_end_fixture_dir / 'outcrop_2d' / 'p13'

    fixture_file = run_directory / 'config.yaml'
    output_file = tmp_path / 'config.yaml'
    create_config_for_legacy_run(
        directory=run_directory,
        config_file=output_file,
        input_file=run_directory / 'p13.dat',  # specified to avoid other test fixtures in folder
        initial_conditions_file=run_directory / 'p13.ini',  # specified to avoid other test fixtures in folder
        final_conditions_file=run_directory / 'p13.fin',  # specified to avoid other test fixtures in folder
        water_properties_file=run_directory / '../../nist120-1800.out',
    )
    RunConfig.from_yaml(output_file)  # loading ensures correct structure
    assert RunConfig.from_yaml(output_file) == RunConfig.from_yaml(fixture_file)
