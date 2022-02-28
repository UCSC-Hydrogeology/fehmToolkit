import pytest

from fehm_toolkit.heat_in import generate_input_heatflux_file


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
def test_against_jdf2d_fixture(tmpdir, matlab_fixture_dir, model_name, model_root):
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
