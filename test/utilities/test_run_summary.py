from fehmtk.postprocessors.run_summary import read_monitored_nodes_from_input


def test_read_monitored_nodes_from_input(fixture_dir):
    nodes = read_monitored_nodes_from_input(fixture_dir / 'simple_input.dat')
    assert nodes == {1, 10, 50, 70, 140}
