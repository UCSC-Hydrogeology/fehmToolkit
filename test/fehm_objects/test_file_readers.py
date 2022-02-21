from fehm_toolkit.fehm_objects import Element
from fehm_toolkit.fehm_objects.grid import read_fehm, read_zones
from fehm_toolkit.fehm_objects.node import Vector


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
    node_numbers_by_zone_number, zone_number_by_name = read_zones(fixture_dir / 'simple_pyramid_outside.zone')
    assert zone_number_by_name == {'top': 1, 'bottom': 2, 'left_w': 3, 'front_s': 4, 'right_e': 5, 'back_n': 6}
    assert node_numbers_by_zone_number == {
        1: (1, 2, 3, 4, 5),
        2: (1, 2, 3, 4),
        3: (1, 4, 5),
        4: (1, 2, 5),
        5: (2, 3, 5),
        6: (3, 4, 5),
    }


def test_read_material_zone_pyramid(fixture_dir):
    node_numbers_by_zone_number, zone_number_by_name = read_zones(fixture_dir / 'simple_pyramid_material.zone')
    assert zone_number_by_name == {}
    assert node_numbers_by_zone_number == {1: (5,), 2: (1, 2, 3, 4)}


def test_read_area_pyramid(fixture_dir):
    areas_by_zone_number, zone_number_by_name = read_zones(fixture_dir / 'simple_pyramid.area')
    assert zone_number_by_name == {'top': 1, 'bottom': 2, 'left_w': 3, 'front_s': 4, 'right_e': 5, 'back_n': 6}
    assert areas_by_zone_number == {
        1: ((-30.0, -30.0, -15.0), (30.0, -30.0, -15.0), (30.0, 30.0, -15.0), (-30.0, 30.0, -15.0), (0.0, 0.0, 40.0)),
        2: ((-30.0, -30.0, -15.0), (30.0, -30.0, -15.0), (30.0, 30.0, -15.0), (-30.0, 30.0, -15.0)),
        3: ((-30.0, -30.0, -15.0), (-30.0, 30.0, -15.0), (0.0, 0.0, 40.0)),
        4: ((-30.0, -30.0, -15.0), (30.0, -30.0, -15.0), (0.0, 0.0, 40.0)),
        5: ((30.0, -30.0, -15.0), (30.0, 30.0, -15.0), (0.0, 0.0, 40.0)),
        6: ((30.0, 30.0, -15.0), (-30.0, 30.0, -15.0), (0.0, 0.0, 40.0)),
    }
