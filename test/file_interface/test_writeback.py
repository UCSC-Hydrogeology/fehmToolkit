import pytest

from fehm_toolkit.file_interface import (
    read_pressure,
    read_restart,
    read_zones,
    write_pressure,
    write_restart,
    write_zones,
)


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


def test_writeback_restart_legacy_format(fixture_dir, tmp_path):
    initial_file = fixture_dir / 'simple_restart_legacy_format.ini'
    output_file = tmp_path / 'out.restart'

    state, metadata = read_restart(initial_file)
    write_restart(state, metadata, output_file)

    assert initial_file.read_text() == output_file.read_text()


def test_writeback_restart_fehm_format(fixture_dir, tmp_path):
    initial_file = fixture_dir / 'simple_restart_fehm_format.fin'
    output_file = tmp_path / 'out.restart'

    state, metadata = read_restart(initial_file)
    write_restart(state, metadata, output_file, fmt='fehm')

    assert initial_file.read_text() == output_file.read_text()


def test_tracer_restart_raises(fixture_dir, tmp_path):
    state, metadata = read_restart(fixture_dir / 'tracer_restart.fin')

    with pytest.raises(NotImplementedError):
        write_restart(state, metadata, tmp_path / 'out.restart')


def test_writeback_pressure(fixture_dir, tmp_path):
    initial_file = fixture_dir / 'square.iap'
    output_file = tmp_path / 'out.iap'

    pressure = read_pressure(initial_file)
    pressure_by_node = {i: pressure for i, pressure in enumerate(pressure)}
    write_pressure(pressure_by_node, output_file=output_file)

    assert initial_file.read_text() == output_file.read_text()
