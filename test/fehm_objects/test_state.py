import pytest

from fehm_toolkit.fehm_objects import State
from fehm_toolkit.fehm_runs.create_run_from_run import replace_node_pressures


@pytest.fixture
def simple_state():
    return State(
        temperature=(1, 2, 3, 4, 5),
        pressure=(1, 2, 3, 4, 5),
    )


def test_replace_node_pressures(simple_state):
    state = replace_node_pressures(
        simple_state,
        replacement_state=State(pressure=(8, 8, 8, 8, 8), temperature=(9, 9, 9, 9, 9)),
        node_numbers=(1, 3, 5),
    )
    assert state == State(
        pressure=(8, 2, 8, 4, 8),
        temperature=(1, 2, 3, 4, 5),
    )


def test_replace_node_pressures_out_of_range(simple_state):
    with pytest.raises(ValueError):
        replace_node_pressures(
            simple_state,
            replacement_state=State(pressure=(8, 8, 8, 8, 8), temperature=(9, 9, 9, 9, 9)),
            node_numbers=(1, 3, 18),
        )


def test_replace_node_pressures_different_sizes(simple_state):
    with pytest.raises(ValueError):
        replace_node_pressures(
            simple_state,
            replacement_state=State(pressure=(7, 8, 9), temperature=(7, 8, 9)),
            node_numbers=(1, 2),
        )
