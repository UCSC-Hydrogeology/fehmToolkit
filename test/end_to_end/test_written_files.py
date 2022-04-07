import logging

import pytest


from fehm_toolkit.heat_in import generate_input_heatflux_file
from fehm_toolkit.rock_properties import generate_rock_properties_files

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
