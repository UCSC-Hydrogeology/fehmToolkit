from fehm_toolkit.fehm_objects import Grid


def test_pyramid_from_fehm(fixture_dir):
    grid = Grid.from_files(fixture_dir / 'simple_pyramid.fehm')
    assert grid.n_nodes == 5
    assert grid.n_elements == 2
    assert grid.element(2).number == 2
    assert grid.node(4).y == 10
