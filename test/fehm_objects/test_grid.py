from pathlib import Path

from fehm_toolkit.fehm_objects import Grid

FIXTURE_DIR = Path(__file__).parent / 'fixtures'


def test_ziggurat_from_fehm():
    grid = Grid.from_fehm(FIXTURE_DIR / 'simple_pyramid.fehm')
    assert grid.n_nodes == 5
    assert grid.n_elements == 2
    assert grid.element(2).number == 2
    assert grid.node(4).y == 10
