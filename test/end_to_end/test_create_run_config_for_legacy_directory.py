from fehm_toolkit.config import RunConfig
from fehm_toolkit.utilities.create_run_config_for_legacy_directory import create_run_config_for_legacy_directory


def test_create_run_config_for_legacy_directory_infer_some(tmp_path, end_to_end_fixture_dir):
    output_file = tmp_path / 'config.yaml'
    create_run_config_for_legacy_directory(
        directory=end_to_end_fixture_dir / 'flat_box' / 'p12',
        config_file=output_file,
        input_file=end_to_end_fixture_dir / 'p12.dat',  # specified to avoid other test fixtures in folder
        final_conditions_file=end_to_end_fixture_dir / 'p12.fin',  # specified to avoid other test fixtures in folder
        water_properties_file=end_to_end_fixture_dir / '../../nist120-1800.out',
    )
    RunConfig.from_yaml(output_file)  # no asserts needed, RunConfig loading ensures correct structure
