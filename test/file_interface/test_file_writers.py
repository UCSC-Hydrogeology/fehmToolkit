from fehm_toolkit.config import FilesConfig

from fehm_toolkit.file_interface import write_files_index


def test_create_files_index(tmp_path):
    output_file = tmp_path / 'run.files'

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
