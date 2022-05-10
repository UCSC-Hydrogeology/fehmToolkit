import pytest

from fehm_toolkit.file_interface import read_zones, write_zones


@pytest.mark.parametrize(
    'initial_filename', (
        'simple_pyramid_outside.zone',
        'simple_pyramid_material.zone',
    )
)
def test_writeback_zone(fixture_dir, tmp_path, initial_filename):
    initial_file = fixture_dir / initial_filename
    output_file = tmp_path / 'out.zone'

    zones = read_zones(initial_file)
    write_zones(zones, output_file)

    assert initial_file.read_text() == output_file.read_text()


def test_write_area_raises(fixture_dir, tmp_path):
    area_zones = read_zones(fixture_dir / 'simple_pyramid.area')

    with pytest.raises(NotImplementedError):
        write_zones(area_zones, tmp_path / 'out.area')
