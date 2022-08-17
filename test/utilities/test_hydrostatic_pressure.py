import numpy as np
import pytest

from fehm_toolkit.preprocessors.hydrostatic_pressure import build_z_column_around_reference


@pytest.mark.parametrize('reference_z, z_interval_m, z_targets, expected', (
    # Reference is below all targets
    (-5, 5, np.array([3, 7, 10]), np.array([10, 5, 0, -5])),
    (-5, 3, np.array([3, 7, 10]), np.array([10, 7, 4, 1, -2, -5])),
    (1, 5, np.array([3, 7, 10]), np.array([11, 6, 1])),

    # Reference is above all targets
    (20, 5, np.array([0, 5, 10, 15]), np.array([20, 15, 10, 5, 0])),
    (20, 5, np.array([3, 8]), np.array([20, 15, 10, 5, 0])),
    (20, 4, np.array([3, 8]), np.array([20, 16, 12, 8, 4, 0])),

    # Reference is amongst targets
    (10, 5, np.array([0, 5, 10, 15]), np.array([15, 10, 5, 0])),
    (12, 5, np.array([0, 5, 10, 15]), np.array([17, 12, 7, 2, -3])),
    (11, 8, np.array([5, 7, 18]), np.array([19, 11, 3])),
    (1, 5, np.array([-4, 7, 10]), np.array([11, 6, 1, -4])),
))
def test_build_z_column_around_reference_reference(reference_z, z_interval_m, z_targets, expected):
    z_column = build_z_column_around_reference(
        z_targets=z_targets,
        params={
            'reference_z': reference_z,
            'z_interval_m': z_interval_m,
        }
    )
    np.testing.assert_array_equal(z_column, expected)
