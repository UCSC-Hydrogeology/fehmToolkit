import logging

from numpy.testing import assert_array_almost_equal
import pytest

from fehm_toolkit.file_interface import read_pressure, write_restart, write_zones
from fehm_toolkit.heat_in import generate_input_heatflux_file
from fehm_toolkit.hydrostatic_pressure import generate_hydrostatic_pressure_file
from fehm_toolkit.rock_properties import generate_rock_properties_files
from fehm_toolkit.file_manipulation.append_zones import append_zones
from fehm_toolkit.file_manipulation.create_restart import create_restart_from_avs, create_restart_from_restart
from fehm_toolkit.file_manipulation.modify_fehm_input_file import write_modified_fehm_input_file

logger = logging.getLogger(__name__)


@pytest.mark.parametrize('mesh_name', ('flat_box', 'outcrop_2d', 'warped_box'))
def test_heat_in_against_fixture(tmp_path, end_to_end_fixture_dir, mesh_name):
    model_dir = end_to_end_fixture_dir / mesh_name / 'cond'
    output_file = tmp_path / 'output.hflx'

    generate_input_heatflux_file(
        config_file=model_dir / 'config.yaml',
        grid_file=model_dir / 'cond.fehm',
        outside_zone_file=model_dir / 'cond_outside.zone',
        area_file=model_dir / 'cond.area',
        output_file=output_file,
    )

    fixture_file = model_dir / 'cond.hflx'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name', ('flat_box', 'outcrop_2d', 'warped_box'))
def test_rock_properties_against_fixture(tmp_path, end_to_end_fixture_dir, mesh_name):
    logger.info(f'Generating rock properties files ({mesh_name}).')
    model_dir = end_to_end_fixture_dir / mesh_name / 'cond'
    generate_rock_properties_files(
        config_file=model_dir / 'config.yaml',
        grid_file=model_dir / 'cond.fehm',
        outside_zone_file=model_dir / 'cond_outside.zone',
        material_zone_file=model_dir / 'cond_material.zone',
        cond_output_file=tmp_path / 'output.cond',
        perm_output_file=tmp_path / 'output.perm',
        ppor_output_file=tmp_path / 'output.ppor',
        rock_output_file=tmp_path / 'output.rock',
    )

    for output_extension in ('cond', 'perm', 'ppor', 'rock'):
        logger.info(f'Comparing output for {output_extension} file.')
        output_file = tmp_path / f'output.{output_extension}'
        fixture_file = model_dir / f'cond.{output_extension}'
        assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name', ('flat_box', 'outcrop_2d', 'warped_box'))
def test_append_zones_against_fixture(tmp_path, end_to_end_fixture_dir, mesh_name):
    model_dir = end_to_end_fixture_dir / mesh_name / 'cond'
    output_file = tmp_path / 'output.zone'
    combined_zones = append_zones(
        zone_keys_to_add=('top', 'bottom'),
        add_zones_from_file=model_dir / 'cond_outside.zone',
        add_zones_to_file=model_dir / 'cond_material.zone',
    )
    write_zones(combined_zones, output_file, include_zone_names=False)

    fixture_file = model_dir / 'cond.zone'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name, model_name, avs_number', (
    ('flat_box', 'p12', 11),
    ('outcrop_2d', 'p13', 2),
))
def test_create_restart_from_avs_against_fixture(tmp_path, end_to_end_fixture_dir, mesh_name, model_name, avs_number):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    state, metadata = create_restart_from_avs(
        avs_file=model_dir / f'{model_name}.{avs_number:05d}_sca_node.avs',
        base_restart_file=model_dir / f'{model_name}.ini',
    )
    output_file = tmp_path / 'test.fin'
    fixture_file = model_dir / 'avs2fin_fixture.fin'

    write_restart(state, metadata, output_file=output_file)

    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'mesh_name, model_name', (
        ('flat_box', 'cond'),
        ('outcrop_2d', 'cond'),
        ('outcrop_2d', 'p13'),
        ('warped_box', 'cond'),
    )
)
def test_create_restart_from_restart_against_fixture(tmp_path, end_to_end_fixture_dir, mesh_name, model_name):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    state, metadata = create_restart_from_restart(model_dir / f'{model_name}.fin', reset_model_time=True)

    output_file = tmp_path / 'test.fin'
    fixture_file = model_dir / 'fin2ini_fixture.ini'

    write_restart(state, metadata, output_file=output_file)

    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'mesh_name, model_name', (
        ('flat_box', 'cond'),
        ('outcrop_2d', 'cond'),
    )
)
def test_create_restart_from_pressure_against_fixture(tmp_path, end_to_end_fixture_dir, mesh_name, model_name):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    state, metadata = create_restart_from_restart(
        base_restart_file=model_dir / f'{model_name}.fin',
        reset_model_time=True,
        pressure_file=model_dir / f'{model_name}.iap'
    )

    output_file = tmp_path / 'test.ini'
    fixture_file = model_dir / 'iap2ini_fixture.ini'

    write_restart(state, metadata, output_file=output_file)

    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'mesh_name, model_name', (
        ('flat_box', 'cond'),
        ('flat_box', 'p12'),
        ('outcrop_2d', 'cond'),
        ('outcrop_2d', 'p13'),
        ('warped_box', 'cond'),
    )
)
def test_write_modified_fehm_input_against_fixture(tmp_path, end_to_end_fixture_dir, mesh_name, model_name):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    output_file = tmp_path / 'test.dat'
    file_extensions = {'perm', 'rock', 'cond', 'ppor', 'hflx', 'flow'}

    write_modified_fehm_input_file(
        base_fehm_input_file=model_dir / f'{model_name}.dat',
        out_file=output_file,
        file_mapping={f'{model_name}.{ext}': f'test.{ext}' for ext in file_extensions},
    )

    fixture_file = model_dir / 'datcopy_fixture.dat'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'mesh_name, model_name', (
        ('flat_box', 'cond'),
        ('flat_box', 'p12'),
        ('outcrop_2d', 'cond'),
        ('outcrop_2d', 'p13'),
        ('warped_box', 'cond'),
    )
)
def test_write_modified_fehm_input_with_timing_against_fixture(tmp_path, end_to_end_fixture_dir, mesh_name, model_name):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    output_file = tmp_path / 'test.dat'

    write_modified_fehm_input_file(
        base_fehm_input_file=model_dir / f'{model_name}.dat',
        out_file=output_file,
        initial_timestep_days=7300,
        initial_simulation_time_days=1234,
    )

    fixture_file = model_dir / 'datreset_fixture.dat'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name', ('flat_box', 'outcrop_2d', 'warped_box'))
def test_generate_hydrostatic_pressure(tmp_path, end_to_end_fixture_dir, mesh_name):
    model_dir = end_to_end_fixture_dir / mesh_name / 'cond'
    output_file = tmp_path / 'test.iap'

    generate_hydrostatic_pressure_file(
        config_file=model_dir / 'config.yaml',
        grid_file=model_dir / 'cond.fehm',
        material_zone_file=model_dir / 'cond_material.zone',
        outside_zone_file=model_dir / 'cond_outside.zone',
        restart_file=model_dir / 'cond.fin',
        water_properties_file=end_to_end_fixture_dir / 'nist120-1800.out',
        output_file=output_file,
    )
    fixture_file = model_dir / 'cond.iap'

    fixture_pressure = read_pressure(fixture_file)
    output_pressure = read_pressure(output_file)
    assert_array_almost_equal(fixture_pressure, output_pressure, 1)
