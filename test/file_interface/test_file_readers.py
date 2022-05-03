from fehm_toolkit.fehm_objects import Element, Vector, Zone
from fehm_toolkit.file_interface import read_fehm, read_zones


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
