import pytest

from fehm_toolkit.fehm_objects import Node, Vector
from fehm_toolkit.file_interface import read_grid


def test_pyramid_from_fehm(fixture_dir):
    grid = read_grid(fixture_dir / 'simple_pyramid.fehm')
    assert grid.n_nodes == 5
    assert grid.n_elements == 2
    assert grid.element(2).number == 2
    assert grid.node(4).y == 10

    with pytest.raises(ValueError):
        next(grid.get_nodes_in_material_zone(1))

    with pytest.raises(ValueError):
        next(grid.get_nodes_in_outside_zone('bottom'))


def test_square_from_fehm(fixture_dir):
    grid = read_grid(fixture_dir / 'square.fehm')
    assert grid.n_nodes == 5
    assert grid.n_elements == 4
    assert grid.element(3).number == 3
    assert grid.node(5).y == 5

    with pytest.raises(ValueError):
        next(grid.get_nodes_in_material_zone(1))

    with pytest.raises(ValueError):
        next(grid.get_nodes_in_outside_zone('bottom'))


@pytest.mark.filterwarnings('ignore:The required storage space exceeds the available storage space.')
def test_pyramid_from_fehm_and_zones(fixture_dir):
    grid = read_grid(
        fixture_dir / 'simple_pyramid.fehm',
        material_zone_file=fixture_dir / 'simple_pyramid_material.zone',
        outside_zone_file=fixture_dir / 'simple_pyramid_outside.zone',
        area_file=fixture_dir / 'simple_pyramid.area',
    )
    assert grid.n_nodes == 5
    assert grid.n_elements == 2

    for node in grid.nodes:
        if node.outside_area:
            assert isinstance(node.outside_area, Vector)

    assert list(grid.get_nodes_in_material_zone(1)) == [
        Node(5, coordinates=Vector(5., 5., 10.), outside_area=Vector(0., 0., 40.), depth=0.0)
    ]

    outside_node_numbers = {node.number for node in grid.get_nodes_in_outside_zone('bottom')}
    assert outside_node_numbers == {1, 2, 3, 4}


def test_square_from_fehm_and_zones(fixture_dir):
    grid = read_grid(
        fixture_dir / 'square.fehm',
        material_zone_file=fixture_dir / 'square_material.zone',
        outside_zone_file=fixture_dir / 'square_outside.zone',
        area_file=fixture_dir / 'square.area',
    )
    assert grid.n_nodes == 5
    assert grid.n_elements == 4

    for node in grid.nodes:
        if node.outside_area:
            assert isinstance(node.outside_area, Vector)

    assert grid.node(3).outside_area.z + grid.node(4).outside_area.z == 10

    assert list(grid.get_nodes_in_material_zone(1)) == [
        Node(3, coordinates=Vector(0., 10., 10.), outside_area=Vector(0., 5., 5.), depth=0.0),
        Node(4, coordinates=Vector(0., 0., 10.), outside_area=Vector(0., -5., 5.), depth=0.0),
    ]
    assert list(grid.get_nodes_in_material_zone(2)) == [
        Node(5, coordinates=Vector(0., 5., 5.), outside_area=None, depth=5.),
    ]
    assert list(grid.get_nodes_in_outside_zone('bottom')) == [
        Node(1, coordinates=Vector(0., 0., 0.), outside_area=Vector(0., -5., -5.), depth=10.0),
        Node(2, coordinates=Vector(0., 10., 0.), outside_area=Vector(0., 5., -5.), depth=10.0),
    ]


def test_validate_mismatched_outside_zone_lookups(fixture_dir):
    with pytest.raises(ValueError):
        read_grid(
            fixture_dir / 'square.fehm',
            material_zone_file=fixture_dir / 'square_material.zone',
            outside_zone_file=fixture_dir / 'square_outside.zone',
            area_file=fixture_dir / 'simple_pyramid.area',
        )
