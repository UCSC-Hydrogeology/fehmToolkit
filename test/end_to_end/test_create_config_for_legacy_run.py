import shutil

from fehm_toolkit.config import RunConfig
from fehm_toolkit.fehm_runs.create_config_for_legacy_run import create_config_for_legacy_run


def test_create_config_for_legacy_run_flat_box(tmp_path, end_to_end_fixture_dir):
    run_directory = end_to_end_fixture_dir / 'flat_box' / 'p12'
    tmp_model_dir = tmp_path / 'root' / 'model' / 'run'
    shutil.copytree(run_directory, tmp_model_dir)
    (tmp_model_dir.parent.parent / 'nist120-1800.out').touch()

    output_file = tmp_model_dir / 'config.yaml'
    fixture_file = tmp_model_dir / 'fixture.yaml'
    output_file.rename(fixture_file)

    create_config_for_legacy_run(
        directory=tmp_model_dir,
        config_file=output_file,
        input_file=tmp_model_dir / 'p12.dat',  # specified to avoid other test fixtures in folder
        final_conditions_file=tmp_model_dir / 'p12.fin',  # specified to avoid other test fixtures in folder
        water_properties_file=tmp_model_dir.parent.parent / 'nist120-1800.out',
    )
    assert RunConfig.from_yaml(output_file) == RunConfig.from_yaml(fixture_file)


def test_create_config_for_legacy_run_outcrop_2d(tmp_path, end_to_end_fixture_dir):
    run_directory = end_to_end_fixture_dir / 'outcrop_2d' / 'p13'
    tmp_model_dir = tmp_path / 'root' / 'model' / 'run'
    shutil.copytree(run_directory, tmp_model_dir)
    (tmp_model_dir.parent.parent / 'nist120-1800.out').touch()

    output_file = tmp_model_dir / 'config.yaml'
    fixture_file = tmp_model_dir / 'config.yaml'
    output_file.rename(fixture_file)

    create_config_for_legacy_run(
        directory=tmp_model_dir,
        config_file=output_file,
        input_file=tmp_model_dir / 'p13.dat',  # specified to avoid other test fixtures in folder
        initial_conditions_file=tmp_model_dir / 'p13.ini',  # specified to avoid other test fixtures in folder
        final_conditions_file=tmp_model_dir / 'p13.fin',  # specified to avoid other test fixtures in folder
        water_properties_file=tmp_model_dir.parent.parent / 'nist120-1800.out',
    )
    assert RunConfig.from_yaml(output_file) == RunConfig.from_yaml(fixture_file)
