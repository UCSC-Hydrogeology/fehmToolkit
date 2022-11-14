from fehmtk.config import FilesConfig
from fehmtk.file_interface import write_files_index


def test_create_files_index(tmp_path):
    output_file = tmp_path / 'run.files'

    files_config = FilesConfig(
        run_root='run_root',
        material_zone=tmp_path / 'material_zone.txt',
        outside_zone=tmp_path / 'outside_zone.txt',
        area=tmp_path / 'area.txt',
        rock_properties=tmp_path / 'rock_properties.txt',
        conductivity=tmp_path / 'conductivity.txt',
        pore_pressure=tmp_path / 'pore_pressure.txt',
        permeability=tmp_path / 'permeability.txt',
        heat_flux=tmp_path / 'heat_flux.txt',
        flow=tmp_path / 'flow.txt',
        files=tmp_path / 'files.txt',
        grid=tmp_path / 'grid.txt',
        input=tmp_path / 'input.txt',
        output=tmp_path / 'output.txt',
        storage=tmp_path / 'store.txt',
        history=tmp_path / 'history.txt',
        water_properties=tmp_path / 'water_properties.txt',
        check=tmp_path / 'check.txt',
        error=tmp_path / 'error.txt',
        final_conditions=tmp_path / 'final_conditions.txt',
    )
    write_files_index(files_config, output_file=output_file)
    assert output_file.read_text() == (
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
