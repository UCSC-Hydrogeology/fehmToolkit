from fehm_toolkit.fehm_objects import Element, State, Vector, Zone
from fehm_toolkit.file_interface import read_fehm, read_restart, read_zones


def test_read_fehm_pyramid(fixture_dir):
    coordinates_by_number, elements_by_number = read_fehm(fixture_dir / 'simple_pyramid.fehm')
    assert coordinates_by_number and elements_by_number

    for node_number, coordinates in coordinates_by_number.items():
        assert isinstance(node_number, int)
        assert isinstance(coordinates, Vector)
        for coor in coordinates.value:
            assert isinstance(coor, float)

    for element_number, element in elements_by_number.items():
        assert isinstance(element_number, int)
        assert isinstance(element, Element)
        for node_number in element.nodes:
            assert node_number in coordinates_by_number
            assert len(element.nodes) == element.connectivity


def test_read_outside_zone_pyramid(fixture_dir):
    outside_zones = read_zones(fixture_dir / 'simple_pyramid_outside.zone')
    assert outside_zones == (
        Zone(number=1, name='top', data=(1, 2, 3, 4, 5)),
        Zone(number=2, name='bottom', data=(1, 2, 3, 4)),
        Zone(number=3, name='left_w', data=(1, 4, 5)),
        Zone(number=5, name='right_e', data=(2, 3, 5)),
        Zone(number=6, name='back_n', data=(3, 4, 5)),
        Zone(number=4, name='front_s', data=(1, 2, 5)),
    )


def test_read_material_zone_pyramid(fixture_dir):
    material_zones = read_zones(fixture_dir / 'simple_pyramid_material.zone')
    assert material_zones == (
        Zone(number=1, name=None, data=(5,)),
        Zone(number=2, name=None, data=(1, 2, 3, 4)),
    )


def test_read_area_pyramid(fixture_dir):
    area_zones = read_zones(fixture_dir / 'simple_pyramid.area')
    assert area_zones == (
        Zone(
            number=1,
            name='top',
            data=(
                Vector(-30.0, -30.0, -15.0),
                Vector(30.0, -30.0, -15.0),
                Vector(30.0, 30.0, -15.0),
                Vector(-30.0, 30.0, -15.0),
                Vector(0.0, 0.0, 40.0),
            ),
        ),
        Zone(
            number=2,
            name='bottom',
            data=(
                Vector(-30.0, -30.0, -15.0),
                Vector(30.0, -30.0, -15.0),
                Vector(30.0, 30.0, -15.0),
                Vector(-30.0, 30.0, -15.0),
            ),
        ),
        Zone(
            number=3,
            name='left_w',
            data=(Vector(-30.0, -30.0, -15.0), Vector(-30.0, 30.0, -15.0), Vector(0.0, 0.0, 40.0)),
        ),
        Zone(
            number=5,
            name='right_e',
            data=(Vector(30.0, -30.0, -15.0), Vector(30.0, 30.0, -15.0), Vector(0.0, 0.0, 40.0)),
        ),
        Zone(
            number=6,
            name='back_n',
            data=(Vector(30.0, 30.0, -15.0), Vector(-30.0, 30.0, -15.0), Vector(0.0, 0.0, 40.0)),
        ),
        Zone(
            number=4,
            name='front_s',
            data=(Vector(-30.0, -30.0, -15.0), Vector(30.0, -30.0, -15.0), Vector(0.0, 0.0, 40.0)),
        ),
    )


def test_read_simple_restart(fixture_dir):
    state, metadata = read_restart(fixture_dir / 'simple_restart.ini')
    assert metadata == {
        'runtime_header': 'FEHM V3.1gf 12-02-29 QA:NA       09/23/2018    02:31:14',
        'model_description': '"Simple restart description"',
        'simulation_time_days': 0,
        'n_nodes': 6,
    }
    assert state == State(
        temperatures=[35.3103156449, 26.3715674828, 26.6993730893, 13.7232584411, 13.4748018922, 9.9921394765],
        saturations=[1.0000000000, 1.0000000000, 1.0000000000, 1.0000000000, 1.0000000000, 1.0000000000],
        pressures=[46.1720206040, 45.6706062299, 45.6811178622, 45.4069398347, 45.3847810418, 45.1548391299],
    )


def test_read_tracer_restart(fixture_dir):
    state, metadata = read_restart(fixture_dir / 'tracer_restart.fin')
    assert metadata == {
        'runtime_header': 'FEHM V3.1gf 12-02-09 QA:NA       02/09/2012    11:48:27',
        'model_description': 'Unsaturated Diffusion tests',
        'simulation_time_days': 5000,
        'n_nodes': 12,
    }
    assert state == State(
        temperatures=[
            34.99999999987494, 34.99999999987494, 29.99740954219060, 29.99740954219060,
            24.99481908388880, 24.99481908388880, 19.99222863160355, 19.99222863160355,
            14.99935303204482, 14.99935303204482, 10.00000000012507, 10.00000000012507,
        ],
        saturations=[
            0.1000000000000000E-98, 0.1000000000000000E-98, 0.1000000000000000E-98, 0.1000000000000000E-98,
            0.1000000000000000E-98, 0.1000000000000000E-98, 0.1727371363921276, 0.1727371363921281,
            0.4344871249926068, 0.4344871249926068, 0.7817833455822488, 0.7817833455822516,
        ],
        pressures=[
            0.1001154694602094, 0.1001154694602094, 0.1001154694628803, 0.1001154694628803,
            0.1001154694707533, 0.1001154694707533, 0.1001154694901246, 0.1001154694901246,
            0.1001154722096991, 0.1001154722096991, 0.1001154822144740, 0.1001154822144740,
        ]
    )
