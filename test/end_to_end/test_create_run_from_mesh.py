from fehm_toolkit.config import FilesConfig
from fehm_toolkit.fehm_runs.create_run_from_mesh import create_run_from_mesh, create_files_index


def test_create_run_from_mesh_flat_box_infer(tmp_path, end_to_end_fixture_dir):
    new_directory = tmp_path / 'new_run'
    create_run_from_mesh(
        mesh_directory=end_to_end_fixture_dir / 'flat_box' / 'mesh',
        run_directory=new_directory,
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
        'files.txt',
    }


def test_create_run_from_mesh_flat_box_infer_run_root(tmp_path, end_to_end_fixture_dir):
    new_directory = tmp_path / 'new_run'
    create_run_from_mesh(
        mesh_directory=end_to_end_fixture_dir / 'flat_box' / 'mesh',
        run_directory=new_directory,
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
        'new_run.files',
    }


def test_create_run_from_mesh_outcrop_explicit_files(tmp_path, end_to_end_fixture_dir):
    mesh_directory = end_to_end_fixture_dir / 'outcrop_2d' / 'mesh'
    new_directory = tmp_path / 'new_run'
    create_run_from_mesh(
        mesh_directory=mesh_directory,
        run_directory=new_directory,
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
        'new_run.files',
    }


def test_create_files_index(tmp_path):
    run_directory = tmp_path / 'run'
    run_directory.mkdir()

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
        files='files.txt',
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
    create_files_index(run_directory, files_config)
    files_index_file = run_directory / 'files.txt'
    assert files_index_file.read_text() == (
        'root: run_root\n'
        'input: input.txt\n'
        'outpu: output.txt\n'
        'grida: grid.txt\n'
        'storo: store.txt\n'
        'rsto: final_conditions.txt\n'
        'error: error.txt\n'
        'check: check.txt\n'
        'zone: material_zone.txt\n'
        'look: water_properties.txt\n'
        'hist: history.txt\n\n'
        'all'
    )

