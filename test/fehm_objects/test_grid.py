import pytest

from fehm_toolkit.fehm_objects import Grid, Node
from fehm_toolkit.fehm_objects.node import Vector


def test_pyramid_from_fehm(fixture_dir):
    grid = Grid.from_files(fixture_dir / 'simple_pyramid.fehm')
    assert grid.n_nodes == 5
    assert grid.n_elements == 2
    assert grid.element(2).number == 2
    assert grid.node(4).y == 10

    with pytest.raises(ValueError):
        next(grid.get_nodes_in_material_zone(1))

    with pytest.raises(ValueError):
        next(grid.get_nodes_in_outside_zone('bottom'))


@pytest.mark.filterwarnings('ignore:The required storage space exceeds the available storage space.')
def test_pyramid_from_fehm_and_zones(fixture_dir):
    grid = Grid.from_files(
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

    first_material_nodes = grid.get_nodes_in_material_zone(1)
    assert list(first_material_nodes) == [
        Node(5, coordinates=Vector(5., 5., 10.), outside_area=Vector(0., 0., 40.), depth=0.0)
    ]

    outside_node_numbers = {node.number for node in grid.get_nodes_in_outside_zone('bottom')}
    assert outside_node_numbers == {1, 2, 3, 4}
