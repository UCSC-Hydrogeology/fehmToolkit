from fehm_toolkit.config import FilesConfig, RunConfig
from fehm_toolkit.fehm_runs import create_run_from_mesh, create_run_from_run
from fehm_toolkit.fehm_runs.create_run_from_mesh import create_template_input_file
from fehm_toolkit.file_interface import read_restart


def test_create_run_from_mesh_flat_box_infer(tmp_path, end_to_end_fixture_dir):
    new_directory = tmp_path / 'new_run'
    create_run_from_mesh(
        mesh_directory=end_to_end_fixture_dir / 'flat_box' / 'mesh',
        target_directory=new_directory,
        water_properties_file=end_to_end_fixture_dir / 'nist120-1800.out',
    )
    new_files = {path.name for path in new_directory.iterdir()}
    assert new_files == {
        'flat_box_outside.zone',
        'nist120-1800.out',
        'flat_box_material.zone',
        'config.yaml',
        'flat_box_outside_vor.area',
        'flat_box.stor',
        'flat_box.fehmn',
        'fehmn.files',
        'input.txt',
    }


def test_create_run_from_mesh_flat_box_infer_run_root(tmp_path, end_to_end_fixture_dir):
    new_directory = tmp_path / 'new_run'
    create_run_from_mesh(
        mesh_directory=end_to_end_fixture_dir / 'flat_box' / 'mesh',
        target_directory=new_directory,
        water_properties_file=end_to_end_fixture_dir / 'nist120-1800.out',
        run_root='new_run',
    )
    new_files = {path.name for path in new_directory.iterdir()}
    assert new_files == {
        'new_run_outside.zone',
        'new_run.wpi',
        'new_run_material.zone',
        'config.yaml',
        'new_run.area',
        'new_run.stor',
        'new_run.fehm',
        'fehmn.files',
        'new_run.dat',
    }


def test_create_run_from_mesh_outcrop_explicit_files(tmp_path, end_to_end_fixture_dir):
    mesh_directory = end_to_end_fixture_dir / 'outcrop_2d' / 'mesh'
    new_directory = tmp_path / 'new_run'
    create_run_from_mesh(
        mesh_directory=mesh_directory,
        target_directory=new_directory,
        water_properties_file=end_to_end_fixture_dir / 'nist120-1800.out',
        run_root='new_run',
        grid_file=mesh_directory / 'outcrop_2d.fehmn',
        store_file=mesh_directory / 'outcrop_2d.stor',
        material_zone_file=mesh_directory / 'outcrop_2d_material.zone',
        outside_zone_file=mesh_directory / 'outcrop_2d_outside.zone',
        area_file=mesh_directory / 'outcrop_2d_outside_vor.area',
    )
    new_files = {path.name for path in new_directory.iterdir()}
    assert new_files == {
        'new_run_outside.zone',
        'new_run.wpi',
        'new_run_material.zone',
        'config.yaml',
        'new_run.area',
        'new_run.stor',
        'new_run.fehm',
        'fehmn.files',
        'new_run.dat',
    }


def test_create_template_input_file(tmp_path):
    output_file = tmp_path / 'test.dat'
    files_config = FilesConfig(
        run_root='run_root',
        material_zone='material_zone.txt',
        outside_zone='outside_zone.txt',
        area='area.txt',
        rock_properties='rock_properties.txt',
        conductivity='conductivity.txt',
        pore_pressure='pore_pressure.txt',
        permeability='permeability.txt',
        heat_flux='heat_flux.txt',
        flow='flow.txt',
        files='fehmn.files',
        grid='grid.txt',
        input='input.txt',
        output='output.txt',
        store='store.txt',
        history='history.txt',
        water_properties='water_properties.txt',
        check='check.txt',
        error='error.txt',
        final_conditions='final_conditions.txt',
    )
    create_template_input_file(files_config, output_file=output_file)
    assert output_file.read_text() == (
        '"Template conductive run - ALL COMMENTS MUST BE REPLACED with real config!"\n'
        'init\n    # init config goes here (pres macro may be used instead)\n'
        'sol\n    -1    -1\n'
        'ctrl\n    # ctrl config goes here\n'
        'time\n    # time config goes here\n'
        'hflx\n    # hflx config for fixed temperature zones goes here\n'
        f'hflx\nfile\n{files_config.heat_flux}\n'
        f'rock\nfile\n{files_config.rock_properties}\n'
        f'cond\nfile\n{files_config.conductivity}\n'
        f'perm\nfile\n{files_config.permeability}\n'
        f'ppor\nfile\n{files_config.pore_pressure}\n'
        'stop\n'
    )


def test_create_run_from_run(tmp_path, end_to_end_fixture_dir):
    run_directory = end_to_end_fixture_dir / 'outcrop_2d' / 'cond'
    run_config_file = run_directory / 'config.yaml'
    new_directory = tmp_path / 'new_run'
    new_config_file = new_directory / 'config.yaml'

    create_run_from_run(run_config_file, new_directory)

    run_config = RunConfig.from_yaml(run_config_file)
    new_config = RunConfig.from_yaml(new_config_file)

    assert new_config.files_config.material_zone.exists()
    assert new_config.files_config.outside_zone.exists()
    assert new_config.files_config.area.exists()
    assert new_config.files_config.rock_properties.exists()
    assert new_config.files_config.conductivity.exists()
    assert new_config.files_config.pore_pressure.exists()
    assert new_config.files_config.permeability.exists()
    assert new_config.files_config.water_properties.exists() and new_config.files_config.water_properties.is_symlink()
    assert new_config.files_config.grid.exists()
    assert new_config.files_config.store.exists()
    assert new_config.files_config.files.exists()
    assert new_config.files_config.input.exists()

    assert new_config.files_config.grid.read_text() == run_config.files_config.grid.read_text()
    assert new_config.files_config.outside_zone.read_text() == run_config.files_config.outside_zone.read_text()
    assert new_config.files_config.area.read_text() == run_config.files_config.area.read_text()
    assert new_config.files_config.rock_properties.read_text() == run_config.files_config.rock_properties.read_text()
    new_initial_state, _ = read_restart(new_config.files_config.initial_conditions)
    run_final_state, _ = read_restart(run_config.files_config.final_conditions)
    assert new_initial_state == run_final_state
