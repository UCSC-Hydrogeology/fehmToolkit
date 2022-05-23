import logging

import pytest

from fehm_toolkit.file_interface import write_restart, write_zones
from fehm_toolkit.heat_in import generate_input_heatflux_file
from fehm_toolkit.rock_properties import generate_rock_properties_files
from fehm_toolkit.utilities import (
    append_zones,
    create_restart_from_avs,
    create_restart_from_restart,
    write_modified_fehm_input_file,
)

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'model_name, model_root',
    (
        # TODO(dustin): replace these with small custom grids
        ('np2d_cond', 'cond'),
        ('np2d_p11', 'run'),
        ('jdf2d_p12', 'p12'),
        ('jdf3d_p12d_g981', 'p12d_g981'),
        ('jdf3d_p12', 'p12'),
        ('jdf3d_conduit_p12', 'p12'),
        ('np3d_cond', 'run'),
    )
)
def test_heat_in_against_fixture(tmpdir, matlab_fixture_dir, model_name, model_root):
    model_dir = matlab_fixture_dir / model_name
    generate_input_heatflux_file(
        config_file=model_dir / f'{model_root}.hfi',
        fehm_file=model_dir / f'{model_root}.fehm',
        outside_zone_file=model_dir / f'{model_root}_outside.zone',
        area_file=model_dir / f'{model_root}.area',
        output_file=tmpdir / 'output.hflx',
    )

    with open(model_dir / f'{model_root}.hflx') as fixture_file:
        expected = fixture_file.read()

    with open(tmpdir / 'output.hflx') as output_file:
        actual = output_file.read()

    assert actual == expected


@pytest.mark.parametrize(
    'model_name, model_root',
    (
        # TODO(dustin): replace these with small custom grids
        ('np2d_cond', 'cond'),
        ('np2d_p11', 'run'),
        ('jdf3d_p12d_g981', 'p12d_g981'),

        # Fails on ppor file due to bugs in fixture version which have been addressed
        # jdf runs also fail on cond due to small expected variation in ctr2tcon calculation
        # ('np3d_cond', 'run'),
        # ('jdf2d_p12', 'p12'),
        # ('jdf3d_p12', 'p12'),
    )
)
def test_rock_properties_against_fixture(tmpdir, matlab_fixture_dir, model_name, model_root):
    logger.info(f'Generating rock properties files ({model_name}).')
    model_dir = matlab_fixture_dir / model_name
    generate_rock_properties_files(
        config_file=model_dir / f'{model_root}.rpi',
        fehm_file=model_dir / f'{model_root}.fehm',
        outside_zone_file=model_dir / f'{model_root}_outside.zone',
        material_zone_file=model_dir / f'{model_root}_material.zone',
        cond_output_file=tmpdir / 'output.cond',
        perm_output_file=tmpdir / 'output.perm',
        ppor_output_file=tmpdir / 'output.ppor',
        rock_output_file=tmpdir / 'output.rock',
    )

    for output_extension in ('cond', 'perm', 'ppor', 'rock'):
        if model_name == 'jdf3d_p12d_g981' and output_extension == 'cond':
            logger.info('Skipping file check (%s, %s), small variation expected.', model_name, output_extension)
            continue

        logger.info(f'Comparing output for {output_extension} file.')
        with open(model_dir / f'{model_root}.{output_extension}') as fixture_file:
            expected = fixture_file.read()

        with open(tmpdir / f'output.{output_extension}') as output_file:
            actual = output_file.read()

        equal = actual == expected
        assert equal


@pytest.mark.parametrize(
    'model_name, model_root',
    (
        # TODO(dustin): replace these with small custom grids
        ('np2d_cond', 'cond'),
        ('np2d_p11', 'run'),
        ('jdf3d_p12d_g981', 'p12d_g981'),
        ('jdf3d_deep_p11ani', 'p11d600efto_GBv10BBv10_g981'),
        ('np3d_cond', 'run'),
        ('np3d_p11', 'run'),
    )
)
def test_append_zones_against_fixture(tmpdir, matlab_fixture_dir, model_name, model_root):
    model_dir = matlab_fixture_dir / model_name
    combined_zones = append_zones(
        zone_keys_to_add=('top', 'bottom'),
        add_zones_from_file=model_dir / f'{model_root}_outside.zone',
        add_zones_to_file=model_dir / f'{model_root}_material.zone',
    )
    write_zones(combined_zones, tmpdir / 'output.zone', include_zone_names=False)

    # Zone file manually fixed with ending newline and longer spacing on node counts for appended zones
    with open(model_dir / f'{model_root}.zone_fixed') as fixture_file:
        expected = fixture_file.read()

    with open(tmpdir / 'output.zone') as output_file:
        actual = output_file.read()

    assert actual == expected


def test_create_restart_from_avs_against_fixture(tmp_path, matlab_fixture_dir):
    model_dir = matlab_fixture_dir / 'jdf2d_p12'
    state, metadata = create_restart_from_avs(
        avs_file=model_dir / 'p12.00014_sca_node.avs',
        base_restart_file=model_dir / 'p12.ini',
    )
    output_file = tmp_path / 'test.fin'
    fixture_file = model_dir / 'avs2fin_fixture.fin'

    write_restart(state, metadata, output_file=output_file)

    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'model_name, model_root', (
        # TODO(dustin): replace these with small custom grids
        ('np2d_cond', 'cond'),
        ('jdf2d_p12', 'p12'),
    )
)
def test_create_restart_from_restart_against_fixture(tmp_path, matlab_fixture_dir, model_name, model_root):
    model_dir = matlab_fixture_dir / model_name
    state, metadata = create_restart_from_restart(model_dir / f'{model_root}.fin', reset_model_time=True)

    output_file = tmp_path / 'test.fin'
    fixture_file = model_dir / 'fin2ini_fixture_1.ini'

    write_restart(state, metadata, output_file=output_file)

    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'model_name, model_root', (
        # TODO(dustin): replace these with small custom grids
        ('np2d_cond', 'cond'),
        ('jdf2d_p12', 'p12'),
    )
)
def test_create_restart_from_pressure_against_fixture(tmp_path, matlab_fixture_dir, model_name, model_root):
    model_dir = matlab_fixture_dir / model_name
    state, metadata = create_restart_from_restart(
        base_restart_file=model_dir / f'{model_root}.fin',
        reset_model_time=True,
        pressure_file=model_dir / f'{model_root}.iap'
    )

    output_file = tmp_path / 'test.fin'
    fixture_file = model_dir / 'iap2ini_fixture.ini'

    write_restart(state, metadata, output_file=output_file)

    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'model_name, model_root', (
        ('np2d_cond', 'cond'),
        ('jdf3d_p12d_g981', 'p12d_g981'),
    )
)
def test_write_modified_fehm_input_against_fixture(tmp_path, matlab_fixture_dir, model_name, model_root):
    model_dir = matlab_fixture_dir / model_name
    output_file = tmp_path / 'test.dat'
    file_extensions = {'perm', 'rock', 'cond', 'ppor', 'hflx', 'flow'}

    write_modified_fehm_input_file(
        base_control_file=model_dir / f'{model_root}.dat',
        out_file=output_file,
        file_mapping={f'{model_root}.{ext}': f'test.{ext}' for ext in file_extensions},
    )

    fixture_file = model_dir / 'datcopy_fixture.dat'
    assert output_file.read_text() == fixture_file.read_text()


@pytest.mark.parametrize(
    'model_name, model_root', (
        ('np2d_cond', 'cond'),
        ('jdf3d_p12d_g981', 'p12d_g981'),
    )
)
def test_write_modified_fehm_input_with_timing_against_fixture(tmp_path, matlab_fixture_dir, model_name, model_root):
    model_dir = matlab_fixture_dir / model_name
    output_file = tmp_path / 'test.dat'

    write_modified_fehm_input_file(
        base_control_file=model_dir / f'{model_root}.dat',
        out_file=output_file,
        initial_timestep_days=7300,
        initial_simulation_time_days=1234,
    )

    fixture_file = model_dir / 'datreset_fixture.dat'
    assert output_file.read_text() == fixture_file.read_text()
