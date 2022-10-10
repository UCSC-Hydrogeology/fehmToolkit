import logging
import os
from pathlib import Path
import shutil

from numpy.testing import assert_array_almost_equal
import pytest

from fehmtk.config import RunConfig
from fehmtk.file_interface import read_pressure, write_restart
from fehmtk.preprocessors import (
    generate_flow_boundaries,
    generate_input_heat_flux,
    generate_hydrostatic_pressure,
    generate_rock_properties,
)
from fehmtk.file_manipulation import (
    append_zones,
    create_restart_from_avs,
    create_restart_from_restart,
    write_modified_fehm_input_file,
)

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'mesh_name, model_name', (
        ('flat_box', 'p12'),
        ('outcrop_2d', 'p13'),
    ),
)
def test_generate_flow_boundaries(tmp_path: Path, end_to_end_fixture_dir: Path, mesh_name: str, model_name: str):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    tmp_model_dir = tmp_path / 'model_dir'

    shutil.copytree(model_dir, tmp_model_dir)
    config_file = tmp_model_dir / 'config.yaml'
    output_file = RunConfig.from_yaml(config_file).files_config.flow
    os.remove(output_file)

    generate_flow_boundaries(config_file)

    fixture_file = model_dir / f'{model_name}.flow'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name', ('flat_box', 'outcrop_2d', 'warped_box'))
def test_heat_in_against_fixture(tmp_path: Path, end_to_end_fixture_dir: Path, mesh_name: str):
    model_dir = end_to_end_fixture_dir / mesh_name / 'cond'
    tmp_model_dir = tmp_path / 'model_dir'

    shutil.copytree(model_dir, tmp_model_dir)
    output_file = RunConfig.from_yaml(tmp_model_dir / 'config.yaml').files_config.heat_flux
    os.remove(output_file)

    generate_input_heat_flux(tmp_model_dir / 'config.yaml')

    fixture_file = model_dir / 'cond.hflx'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name', ('flat_box', 'outcrop_2d', 'warped_box'))
def test_rock_properties_against_fixture(tmp_path: Path, end_to_end_fixture_dir: Path, mesh_name: str):
    logger.info(f'Generating rock properties files ({mesh_name}).')
    model_dir = end_to_end_fixture_dir / mesh_name / 'cond'

    tmp_model_dir = tmp_path / 'model_dir'
    shutil.copytree(model_dir, tmp_model_dir)
    for output_extension in ('cond', 'perm', 'ppor', 'rock'):
        os.remove(tmp_model_dir / f'cond.{output_extension}')

    generate_rock_properties(tmp_model_dir / 'config.yaml')

    for output_extension in ('cond', 'perm', 'ppor', 'rock'):
        logger.info(f'Comparing output for {output_extension} file.')
        output_file = tmp_model_dir / f'cond.{output_extension}'
        fixture_file = model_dir / f'cond.{output_extension}'
        assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name', ('flat_box', 'outcrop_2d', 'warped_box'))
def test_append_zones_against_fixture(tmp_path: Path, end_to_end_fixture_dir: Path, mesh_name: str):
    model_dir = end_to_end_fixture_dir / mesh_name / 'cond'
    output_file = tmp_path / 'output.zone'
    shutil.copy(model_dir / 'cond_material.zone', output_file)

    append_zones(source_file=model_dir / 'cond_outside.zone', target_file=output_file, zones=('top', 'bottom'))
    fixture_file = model_dir / 'cond.zone'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name, model_name, avs_number', (
    ('flat_box', 'p12', 11),
    ('outcrop_2d', 'p13', 2),
))
def test_create_restart_from_avs_against_fixture(
    tmp_path: Path,
    end_to_end_fixture_dir: Path,
    mesh_name: str,
    model_name: str,
    avs_number: int,
):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    state, metadata = create_restart_from_avs(
        avs_file=model_dir / f'{model_name}.{avs_number:05d}_sca_node.avs',
        base_restart_file=model_dir / f'{model_name}.ini',
    )
    output_file = tmp_path / 'test.fin'
    fixture_file = model_dir / 'avs2fin.fin_fixture'

    write_restart(state, metadata, output_file=output_file, fmt='legacy')

    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'mesh_name, model_name', (
        ('flat_box', 'cond'),
        ('outcrop_2d', 'cond'),
        ('outcrop_2d', 'p13'),
        ('warped_box', 'cond'),
    )
)
def test_create_restart_from_restart_against_fixture(
    tmp_path: Path,
    end_to_end_fixture_dir: Path,
    mesh_name: str,
    model_name: str,
):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    state, metadata = create_restart_from_restart(model_dir / f'{model_name}.fin', reset_model_time=True)

    output_file = tmp_path / 'test.fin'
    fixture_file = model_dir / 'fin2ini.ini_fixture'

    write_restart(state, metadata, output_file=output_file, fmt='legacy')

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
    fixture_file = model_dir / 'iap2ini.ini_fixture'

    write_restart(state, metadata, output_file=output_file, fmt='legacy')

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
def test_write_modified_fehm_input_against_fixture(
    tmp_path: Path,
    end_to_end_fixture_dir: Path,
    mesh_name: str,
    model_name: str,
):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    output_file = tmp_path / 'test.dat'
    file_extensions = {'perm', 'rock', 'cond', 'ppor', 'hflx', 'flow'}

    write_modified_fehm_input_file(
        base_input_file=model_dir / f'{model_name}.dat',
        output_file=output_file,
        file_mapping={f'{model_name}.{ext}': f'test.{ext}' for ext in file_extensions},
    )

    fixture_file = model_dir / 'datcopy.dat_fixture'
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
def test_write_modified_fehm_input_with_timing_against_fixture(
    tmp_path: Path,
    end_to_end_fixture_dir: Path,
    mesh_name: str,
    model_name: str,
):
    model_dir = end_to_end_fixture_dir / mesh_name / model_name
    output_file = tmp_path / 'test.dat'

    write_modified_fehm_input_file(
        base_input_file=model_dir / f'{model_name}.dat',
        output_file=output_file,
        initial_timestep_days=7300,
        initial_simulation_time_days=1234,
    )

    fixture_file = model_dir / 'datreset.dat_fixture'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize('mesh_name', ('flat_box', 'outcrop_2d', 'warped_box'))
def test_generate_hydrostatic_pressure(tmp_path: Path, end_to_end_fixture_dir: Path, mesh_name: str):
    model_dir = end_to_end_fixture_dir / mesh_name / 'cond'
    output_file = tmp_path / 'test.iap'

    generate_hydrostatic_pressure(model_dir / 'config.yaml', output_file=output_file)
    fixture_file = model_dir / 'cond.iap'

    fixture_pressure = read_pressure(fixture_file)
    output_pressure = read_pressure(output_file)
    assert_array_almost_equal(fixture_pressure, output_pressure, 1)
