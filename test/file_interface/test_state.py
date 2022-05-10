import pytest

from fehm_toolkit.fehm_objects import State


def test_state_same_length():
    State(temperatures=[1, 2, 3], pressures=[0, 5, 6])


def test_state_different_length():
    with pytest.raises(ValueError):
        State(temperatures=[1, 2, 3], pressures=[0, 5, 6], saturations=[0, 1])
