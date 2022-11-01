import pytest

from fehmtk.fehm_objects import State
from fehmtk.fehm_runs.create_run_from_run import replace_node_pressures


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


def test_subtract_states_happy_case(simple_state):
    other = State(temperature=(5, 4, 3, 2, 1), pressure=(3, 3, 3, 3, 3))
    assert simple_state - other == State(temperature=(-4, -2, 0, 2, 4), pressure=(-2, -1, 0, 1, 2))


def test_subtract_states_optional_data(simple_state):
    other = State(temperature=(3, 3, 3, 3, 3), pressure=(1, 1, 1, 1, 1), saturation=(1, 1, 1, 1, 1))
    assert simple_state - other == State(temperature=(-2, -1, 0, 1, 2), pressure=(0, 1, 2, 3, 4))


def test_subtract_states_incompatible_fails(simple_state):
    incompatible = State(temperature=(3, 3), pressure=(1, 1))
    with pytest.raises(ValueError):
        simple_state - incompatible
