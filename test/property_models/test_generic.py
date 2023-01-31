import pytest

from fehmtk.fehm_objects import Vector
from fehmtk.config import ModelConfig
from fehmtk.property_models.generic import constant


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (0, {'constant': 5}, 5),
        (20, {'constant': 5}, 5),
        (20, {'constant': 8}, 8),
    ),
)
def test_constant(depth, params, expected):
    value = constant(
        depth,
        model_config_by_property_kind={'property_kind': ModelConfig('constant', params)},
        property_kind='property_kind',
    )
    assert value == expected


@pytest.mark.parametrize(
    'depth, params, expected',
    (
        (0, {'constant': 5}, Vector(5, 5, 5)),
        (20, {'constant': 5}, Vector(5, 5, 5)),
        (20, {'constant': 8}, Vector(8, 8, 8)),
    ),
)
def test_constant_vector(depth, params, expected):
    value = constant(
        depth,
        model_config_by_property_kind={'permeability': ModelConfig('constant', params)},
        property_kind='permeability',
    )
    assert value == expected
