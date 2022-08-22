from fehm_toolkit.config import RunConfig
from fehm_toolkit.utilities.create_run_config_for_legacy_directory import create_run_config_for_legacy_directory


def test_create_run_config_for_legacy_directory_infer_some(tmp_path, end_to_end_fixture_dir):
    output_file = tmp_path / 'config.yaml'
    run_directory = end_to_end_fixture_dir / 'flat_box' / 'p12'
    create_run_config_for_legacy_directory(
        directory=run_directory,
        config_file=output_file,
        input_file=run_directory / 'p12.dat',  # specified to avoid other test fixtures in folder
        final_conditions_file=run_directory / 'p12.fin',  # specified to avoid other test fixtures in folder
        water_properties_file=run_directory / '../../nist120-1800.out',
    )
    RunConfig.from_yaml(output_file)  # no asserts needed, RunConfig loading ensures correct structure
