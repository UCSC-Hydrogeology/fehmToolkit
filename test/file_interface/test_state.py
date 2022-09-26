import pytest

from fehmtk.fehm_objects import State


def test_state_same_length():
    State(temperature=[1, 2, 3], pressure=[0, 5, 6])


def test_state_different_length():
    with pytest.raises(ValueError):
        State(temperature=[1, 2, 3], pressure=[0, 5, 6], saturation=[0, 1])
